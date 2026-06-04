const sourceOptions = document.getElementById('sourceOptions');
const keywordInput = document.getElementById('keywordInput');
const districtSelect = document.getElementById('districtSelect');
const startBtn = document.getElementById('startScrape');
const stopBtn = document.getElementById('stopScrape');
const statusBadge = document.getElementById('statusBadge');
const logList = document.getElementById('logList');

function log(message) {
  if (!logList) return;
  const item = document.createElement('li');
  item.textContent = message;
  logList.prepend(item);
}

function setStatus(text, type) {
  if (!statusBadge) return;
  statusBadge.textContent = text;
  statusBadge.className = 'badge ' + (type || 'badge-info');
}

if (startBtn) {
  startBtn.addEventListener('click', async () => {
    const sources = Array.from(sourceOptions.querySelectorAll('input:checked')).map((box) => box.value);
    setStatus('Collecting…', 'badge-live');
    log(`Starting collection for ${sources.join(', ')} with keyword "${keywordInput.value}".`);
    try {
      const response = await fetch('/api/collect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sources,
          keyword: keywordInput.value,
          district: districtSelect.value,
        }),
      });
      const data = await response.json();
      setStatus('Completed', 'badge-info');
      log(`${data.message} Saved ${data.records_saved} records.`);
    } catch (error) {
      setStatus('Error', 'badge-warn');
      log('Collection failed: ' + error.message);
    }
  });
}

if (stopBtn) {
  stopBtn.addEventListener('click', () => {
    setStatus('Stopped', 'badge-warn');
    log('Collection stopped by the user.');
  });
}
