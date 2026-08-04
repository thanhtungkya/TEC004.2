/**
 * @file dashboard.js
 * @description Dashboard metric cards updater script.
 *
 * @features
 * - Fetches high-level summary metrics from /api/summary
 * - Formats and populates total listings, average price, and average area cards
 *
 * @dependencies
 * - API endpoint: /api/summary
 */

async function loadSummary() {

  try {
    const response = await fetch('/api/summary');
    const data = await response.json();
    const total = document.getElementById('total-listings');
    const price = document.getElementById('avg-price');
    const area = document.getElementById('avg-area');
    if (total) total.textContent = data.total_listings ?? 0;
    if (price) price.textContent = `${Number(data.avg_price ?? 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
    if (area) area.textContent = `${Number(data.avg_area ?? 0).toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
  } catch (error) {
    console.error('Summary load failed', error);
  }
}

loadSummary();
