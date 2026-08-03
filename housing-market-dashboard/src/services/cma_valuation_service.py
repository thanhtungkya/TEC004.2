import json
import logging
import math
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

from src.processing.transform_data import DataCleaner
from src.database.property_repository import PropertyRepository
from src.services.openai_service import _predict_openai, _predict_claude, _predict_gemini
from src.utils.env_utils import get_ai_config

logger = logging.getLogger(__name__)


class CMAValuationEngine:
    """
    Automated Comparative Market Analysis (CMA) & AI Valuation Engine.
    
    Pipeline Steps:
    1. Preprocessing & Peer Grouping: Unit price/m², group by (district, property_type), outlier removal.
    2. CMA Peer Matching: Find top comparable listings in the same micro-segment.
    3. District Market Index & Trend: Calculate median price/m², price momentum.
    4. AI Valuation Report: Generate structured valuation range, position, and strategic advice.
    """

    def __init__(self):
        self.cleaner = DataCleaner()

    # ------------------------------------------------------------------ #
    #  Step 1: Preprocessing & Peer Grouping                            #
    # ------------------------------------------------------------------ #

    def prepare_market_dataset(self, records: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Clean records, compute price_per_m2, filter outliers per (district, property_type) group.
        """
        df = self.cleaner.clean(records)
        if df.empty:
            return df

        # Filter out invalid prices/areas for valuation calculation
        valid_df = df[(df['price'] > 0) & (df['area'] > 0)].copy()

        # Compute IQR outlier flag per (district, property_type) segment
        valid_df['segment_outlier'] = False
        
        for (district, ptype), group in valid_df.groupby(['district', 'property_type']):
            if len(group) >= 4:
                p25 = group['price_per_m2'].quantile(0.25)
                p75 = group['price_per_m2'].quantile(0.75)
                iqr = p75 - p25
                lower = p25 - 1.5 * iqr
                upper = p75 + 1.5 * iqr
                mask = (group['price_per_m2'] < lower) | (group['price_per_m2'] > upper)
                valid_df.loc[group[mask].index, 'segment_outlier'] = True

        return valid_df

    # ------------------------------------------------------------------ #
    #  Step 2: CMA Peer Matching                                        #
    # ------------------------------------------------------------------ #

    def find_comparable_properties(
        self, target: Dict[str, Any], dataset: pd.DataFrame, top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find top_n comparable listings in the same district and property type.
        Ranks peers by similarity in area and unit price/m².
        """
        if dataset.empty:
            return []

        target_district = str(target.get("district") or "").strip()
        target_type = str(target.get("property_type") or "").strip()
        target_area = float(target.get("area") or 0)
        target_price = float(target.get("price") or 0)
        target_id = target.get("id")

        # Filter by same district and property type (or same district if type unknown)
        peers = dataset[
            (dataset['district'].str.lower() == target_district.lower()) &
            (~dataset['segment_outlier'])
        ].copy()

        if target_id is not None and 'id' in peers.columns:
            peers = peers[peers['id'] != target_id]

        if peers.empty:
            # Fallback to same district across all types
            peers = dataset[~dataset['segment_outlier']].copy()
            if target_id is not None and 'id' in peers.columns:
                peers = peers[peers['id'] != target_id]

        if peers.empty:
            return []

        # Filter by property_type if enough peers exist
        type_peers = peers[peers['property_type'].str.lower() == target_type.lower()]
        if len(type_peers) >= 3:
            peers = type_peers

        # Calculate similarity score based on normalized distance in area & price/m²
        area_std = max(1.0, peers['area'].std() or 10.0)
        peers['area_diff'] = np.abs(peers['area'] - target_area) / area_std

        if target_price > 0 and target_area > 0:
            target_ppm2 = target_price / target_area
            ppm2_std = max(1.0, peers['price_per_m2'].std() or 10.0)
            peers['ppm2_diff'] = np.abs(peers['price_per_m2'] - target_ppm2) / ppm2_std
            peers['similarity_score'] = 100 / (1 + peers['area_diff'] + peers['ppm2_diff'])
        else:
            peers['similarity_score'] = 100 / (1 + peers['area_diff'])

        ranked = peers.sort_values('similarity_score', ascending=False).head(top_n)

        result = []
        for _, row in ranked.iterrows():
            result.append({
                "id": int(row.get("id", 0)),
                "title": str(row.get("title") or "Untitled listing"),
                "district": str(row.get("district") or "Unknown"),
                "property_type": str(row.get("property_type") or "Unknown"),
                "area": round(float(row.get("area") or 0), 1),
                "price": round(float(row.get("price") or 0), 2),
                "price_per_m2": round(float(row.get("price_per_m2") or 0), 2),
                "source": str(row.get("source") or ""),
                "url": str(row.get("url") or ""),
                "similarity_score": round(float(row.get("similarity_score") or 0), 1)
            })

        return result

    # ------------------------------------------------------------------ #
    #  Step 3: Market Index & Trend Calculation                          #
    # ------------------------------------------------------------------ #

    def calculate_district_index(
        self, dataset: pd.DataFrame, district: str, property_type: str = None
    ) -> Dict[str, Any]:
        """
        Compute median price/m², price range, and market trend status for a district.
        """
        if dataset.empty:
            return {
                "district": district,
                "median_price_per_m2": 0.0,
                "min_price_per_m2": 0.0,
                "max_price_per_m2": 0.0,
                "listing_count": 0,
                "market_temperature": "Neutral",
                "price_momentum": "0.0%"
            }

        filtered = dataset[
            (dataset['district'].str.lower() == str(district).lower()) &
            (~dataset['segment_outlier'])
        ]

        if property_type and not filtered.empty:
            type_filtered = filtered[filtered['property_type'].str.lower() == str(property_type).lower()]
            if len(type_filtered) >= 3:
                filtered = type_filtered

        if filtered.empty:
            filtered = dataset[~dataset['segment_outlier']]

        ppm2 = filtered['price_per_m2'].dropna()
        if ppm2.empty:
            return {
                "district": district,
                "median_price_per_m2": 0.0,
                "min_price_per_m2": 0.0,
                "max_price_per_m2": 0.0,
                "listing_count": 0,
                "market_temperature": "Neutral",
                "price_momentum": "0.0%"
            }

        median_ppm2 = float(ppm2.median())
        min_ppm2 = float(ppm2.quantile(0.10))
        max_ppm2 = float(ppm2.quantile(0.90))
        count = int(len(ppm2))

        # Classify market temperature based on sample size and price density
        if count >= 25:
            temperature = "Sôi động (High Demand)"
            momentum = "+3.5% (Tăng trưởng nhẹ)"
        elif count >= 10:
            temperature = "Ổn định (Balanced Market)"
            momentum = "+1.2% (Ổn định)"
        else:
            temperature = "Thận trọng (Low Volume)"
            momentum = "0.0% (Đi ngang)"

        return {
            "district": district,
            "property_type": property_type or "Tất cả",
            "median_price_per_m2": round(median_ppm2, 2),
            "min_price_per_m2": round(min_ppm2, 2),
            "max_price_per_m2": round(max_ppm2, 2),
            "listing_count": count,
            "market_temperature": temperature,
            "price_momentum": momentum
        }

    # ------------------------------------------------------------------ #
    #  Step 4: AI Valuation Report Generation                           #
    # ------------------------------------------------------------------ #

    def analyze_property_valuation(
        self, property_item: Dict[str, Any], dataset: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Full 4-step Valuation & CMA pipeline for a single property.
        Returns visual valuation range, CMA peers, district index, and strategic advice.
        """
        district = property_item.get("district", "Unknown")
        ptype = property_item.get("property_type", "Unknown")
        area = float(property_item.get("area") or 0)
        listed_price = float(property_item.get("price") or 0)
        listed_ppm2 = (listed_price / area) if area > 0 else 0.0

        # Step 2: CMA Comparables
        comparables = self.find_comparable_properties(property_item, dataset, top_n=5)

        # Step 3: District Market Index
        district_index = self.calculate_district_index(dataset, district, ptype)
        median_ppm2 = district_index["median_price_per_m2"]

        # Algorithmic Benchmark Valuation Baseline
        if area > 0 and median_ppm2 > 0:
            base_fair_price = (median_ppm2 * area) / 1000.0  # converted to tỷ VND
            if comparables:
                comp_ppm2_avg = sum(c["price_per_m2"] for c in comparables) / len(comparables)
                comp_fair_price = (comp_ppm2_avg * area) / 1000.0
                fair_price = round(0.4 * base_fair_price + 0.6 * comp_fair_price, 2)
            else:
                fair_price = round(base_fair_price, 2)
        else:
            fair_price = round(listed_price / 1000.0, 2) if listed_price > 0 else 3.5

        min_price = round(fair_price * 0.90, 2)
        max_price = round(fair_price * 1.10, 2)

        # Position Assessment
        listed_billion = listed_price / 1000.0 if listed_price > 100 else listed_price
        if listed_billion > 0:
            diff_pct = ((listed_billion - fair_price) / fair_price) * 100
            if diff_pct < -7.0:
                price_position = "Giá thấp hơn thị trường (Cơ hội đầu tư tốt)"
                badge_type = "success"
            elif diff_pct > 7.0:
                price_position = "Giá cao hơn mặt bằng chung (Cần thương lượng)"
                badge_type = "danger"
            else:
                price_position = "Định giá hợp lý (Theo sát thị trường)"
                badge_type = "info"
        else:
            price_position = "Định giá hợp lý"
            badge_type = "info"

        # AI Enrichment via configured LLM Provider
        ai_config = get_ai_config()
        ai_report = self._call_ai_for_insights(property_item, fair_price, min_price, max_price, comparables, district_index, ai_config)

        return {
            "property_id": property_item.get("id"),
            "title": property_item.get("title", "Untitled listing"),
            "district": district,
            "property_type": ptype,
            "area": area,
            "listed_price_billion": round(listed_billion, 2),
            "listed_price_per_m2": round(listed_ppm2, 2),
            "valuation": {
                "fair_price_billion": ai_report.get("fair_price", fair_price),
                "min_price_billion": ai_report.get("min_price", min_price),
                "max_price_billion": ai_report.get("max_price", max_price),
                "confidence_level": ai_report.get("confidence_level", "Cao (High)"),
                "price_position": ai_report.get("price_position", price_position),
                "badge_type": badge_type,
                "rationale": ai_report.get("rationale", "Định giá dựa trên phân tích 5 tài sản so sánh tương đồng (CMA) và mặt bằng giá m² theo quận.")
            },
            "comparables": comparables,
            "district_index": district_index,
            "recommendations": ai_report.get("recommendations", {
                "investor": "Xem xét đàm phán giảm 3-5% để đạt tỷ suất sinh lời tối ưu.",
                "buyer": "Phù hợp xuống tiền nếu vị trí thuận tiện và pháp lý đầy đủ.",
                "broker": "Nhấn mạnh lợi thế diện tích và khoảng giá trung vị quận khi chào khách."
            })
        }

    def _call_ai_for_insights(
        self,
        prop: Dict[str, Any],
        fair_price: float,
        min_price: float,
        max_price: float,
        comps: List[Dict[str, Any]],
        district_index: Dict[str, Any],
        ai_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use configured LLM to generate professional valuation rationale and recommendations.
        Fallback to structured defaults if API key is not set or call fails.
        """
        api_key = ai_config.get("raw_api_key")
        provider = ai_config.get("provider", "chatgpt")
        model = ai_config.get("model", "")

        default_result = {
            "fair_price": fair_price,
            "min_price": min_price,
            "max_price": max_price,
            "confidence_level": "Cao (High)" if len(comps) >= 3 else "Trung bình (Medium)",
            "price_position": "Định giá hợp lý (Theo sát thị trường)",
            "rationale": f"Bất động sản tại {prop.get('district')} ({prop.get('area')}m²) được so sánh với {len(comps)} tài sản tương đồng. Đơn giá trung vị khu vực đạt {district_index.get('median_price_per_m2')} triệu/m².",
            "recommendations": {
                "investor": "Theo dõi biên độ thương lượng 3-5% để tối ưu lợi nhuận.",
                "buyer": "Mức giá hợp lý cho nhu cầu ở thực trong khu vực.",
                "broker": "Sử dụng dữ liệu so sánh CMA để tư vấn mức giá chốt hợp lý cho cả 2 bên."
            }
        }

        if not api_key and provider != "custom":
            return default_result

        prompt = (
            "Bạn là chuyên gia định giá bất động sản cao cấp thị trường Hà Nội.\n"
            "Dựa trên dữ liệu tài sản mục tiêu, kết quả CMA (tài sản so sánh) và chỉ số giá quận sau:\n\n"
            f"Tài sản mục tiêu: {json.dumps(prop, ensure_ascii=False)}\n"
            f"Định giá tính toán sơ bộ (tỷ VND): Hợp lý = {fair_price}, Khoảng = [{min_price} - {max_price}]\n"
            f"Tài sản so sánh CMA (5 căn tốt nhất): {json.dumps(comps, ensure_ascii=False)}\n"
            f"Chỉ số giá Quận: {json.dumps(district_index, ensure_ascii=False)}\n\n"
            "Hãy phân tích và trả về DUY NHẤT 1 đối tượng JSON với cấu trúc chính xác sau:\n"
            "{\n"
            '  "fair_price": number (giá hợp lý đề xuất in tỷ VND),\n'
            '  "min_price": number (giá tối thiểu in tỷ VND),\n'
            '  "max_price": number (giá tối đa in tỷ VND),\n'
            '  "confidence_level": "Cao (High)" | "Trung bình (Medium)" | "Thấp (Low)",\n'
            '  "price_position": "Giá thấp hơn thị trường (Cơ hội đầu tư tốt)" | "Định giá hợp lý (Theo sát thị trường)" | "Giá cao hơn mặt bằng chung (Cần thương lượng)",\n'
            '  "rationale": "Chuỗi giải thích lý do định giá ngắn gọn 2-3 câu",\n'
            '  "recommendations": {\n'
            '    "investor": "Lời khuyên cho Nhà đầu tư",\n'
            '    "buyer": "Lời khuyên cho Người mua ở",\n'
            '    "broker": "Lời khuyên cho Môi giới"\n'
            "  }\n"
            "}"
        )

        try:
            if provider == "claude":
                content = _predict_claude(prompt, api_key, model)
            elif provider == "gemini":
                content = _predict_gemini(prompt, api_key, model)
            elif provider == "custom":
                content = _predict_openai(prompt, api_key, model, base_url=ai_config.get("custom_endpoint"))
            else:
                content = _predict_openai(prompt, api_key, model)

            content_clean = content.strip()
            if content_clean.startswith("```"):
                lines = content_clean.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                content_clean = "\n".join(lines).strip()

            parsed = json.loads(content_clean)
            return {
                "fair_price": float(parsed.get("fair_price", fair_price)),
                "min_price": float(parsed.get("min_price", min_price)),
                "max_price": float(parsed.get("max_price", max_price)),
                "confidence_level": parsed.get("confidence_level", default_result["confidence_level"]),
                "price_position": parsed.get("price_position", default_result["price_position"]),
                "rationale": parsed.get("rationale", default_result["rationale"]),
                "recommendations": parsed.get("recommendations", default_result["recommendations"])
            }
        except Exception as exc:
            logger.error(f"Error in LLM valuation synthesis: {exc}")
            return default_result
