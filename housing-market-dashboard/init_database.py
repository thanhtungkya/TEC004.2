#!/usr/bin/env python3
"""
Script để khởi tạo SQLite database và tạo bảng.
Có thể chạy độc lập không cần chạy ứng dụng chính.

Usage:
    python init_database.py
"""

import sqlite3
from pathlib import Path

# Định nghĩa đường dẫn database
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "database"
DB_PATH = DB_DIR / "housing_market.db"


def init_database():
    """Khởi tạo database và tạo bảng properties."""
    
    # Tạo thư mục nếu chưa tồn tại
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Thư mục database: {DB_DIR}")
    print(f"📄 Đường dẫn database: {DB_PATH}")
    
    # Kết nối tới database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Tạo bảng properties
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                district TEXT,
                address TEXT,
                price REAL,
                price_text TEXT,
                area REAL,
                area_text TEXT,
                property_type TEXT,
                listing_date TEXT,
                source TEXT,
                url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_district ON properties(district);
            CREATE INDEX IF NOT EXISTS idx_property_type ON properties(property_type);
            CREATE INDEX IF NOT EXISTS idx_created_at ON properties(created_at);
            """
        )
        
        conn.commit()
        print("✅ Database đã được khởi tạo thành công!")
        print("✅ Bảng 'properties' đã được tạo!")
        
        # Hiển thị thông tin bảng
        cursor.execute("PRAGMA table_info(properties)")
        columns = cursor.fetchall()
        
        print("\n📋 Danh sách các cột trong bảng 'properties':")
        print("-" * 60)
        for col in columns:
            print(f"  • {col[1]:<15} | {col[2]:<15} | NULL: {col[3]} | Default: {col[4]}")
        print("-" * 60)
        
        # Kiểm tra số lượng bản ghi hiện có
        cursor.execute("SELECT COUNT(*) FROM properties")
        count = cursor.fetchone()[0]
        print(f"\n📊 Số lượng bản ghi hiện tại: {count}")
        
    except sqlite3.Error as e:
        print(f"❌ Lỗi database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🗄️  KHỞI TẠO SQLITE DATABASE")
    print("=" * 60)
    init_database()
    print("=" * 60)
