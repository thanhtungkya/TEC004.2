const sourceOptions = document.getElementById('sourceOptions');
const keywordInput = document.getElementById('keywordInput');
const districtSelect = document.getElementById('districtSelect');
const startBtn = document.getElementById('startScrape');
const stopBtn = document.getElementById('stopScrape');
const statusBadge = document.getElementById('statusBadge');
const logList = document.getElementById('logList');
const selectedSourceCount = document.getElementById('selectedSourceCount');
const selectedDistrictLabel = document.getElementById('selectedDistrictLabel');
const recordsSavedLabel = document.getElementById('recordsSavedLabel');

function selectedSources() {
  if (!sourceOptions) return [];
  return Array.from(sourceOptions.querySelectorAll('input:checked')).map((box) => box.value);
}

function updateRunSummary(recordsSaved) {
  if (selectedSourceCount) selectedSourceCount.textContent = selectedSources().length;
  if (selectedDistrictLabel) selectedDistrictLabel.textContent = districtSelect?.value || 'All';
  if (recordsSavedLabel && recordsSaved !== undefined) recordsSavedLabel.textContent = recordsSaved;
}

function log(message) {
  if (!logList) return;
  if (logList.children.length === 1 && logList.firstElementChild?.classList.contains('muted')) {
    logList.innerHTML = '';
  }
  const item = document.createElement('li');
  item.textContent = message;
  logList.prepend(item);
}

function setStatus(text, type) {
  if (!statusBadge) return;
  statusBadge.textContent = text;
  statusBadge.className = 'badge ' + (type || 'badge-info');
}

let pollInterval = null;
let lastLogCount = 0;


async function checkProgress() {
  try {
    const res = await fetch('/api/scraper-status');
    const data = await res.json();
    
    updateRunSummary(data.records_saved ?? 0);

    if (data.progress) {
      const allSources = ['Alonhadat', 'Homedy', 'Nhadat24h', 'batdongsan', 'mogi', 'nhatot', 'sosanhnha', 'bds123', 'nhaongay', 'meeyland', '123nhadatviet'];
      allSources.forEach(src => {
        if (document.getElementById('progress' + src) && data.progress[src.toLowerCase()] !== undefined) {
          document.getElementById('progress' + src).style.width = Math.min(100, (data.progress[src.toLowerCase()]/200)*100) + '%';
          if (document.getElementById('count' + src)) {
            document.getElementById('count' + src).textContent = data.progress[src.toLowerCase()] + ' / 200';
          }
        }
      });
    }

    if (data.logs && data.logs.length > lastLogCount) {
      for (let i = lastLogCount; i < data.logs.length; i++) {
        const l = data.logs[i];
        const item = document.createElement('li');
        let badgeClass = 'badge-info';
        if (l.status === 'Success') badgeClass = 'badge-success';
        if (l.status === 'Fail') badgeClass = 'badge-warn';
        item.innerHTML = `<span class="muted">[${l.time}]</span> <strong>${l.source}</strong>: <span class="badge ${badgeClass}" style="margin-left:4px; margin-right:4px;">${l.status}</span> ${l.message}`;
        logList.prepend(item);
      }
      lastLogCount = data.logs.length;
    }
    
    if (!data.is_running) {
      clearInterval(pollInterval);
      setStatus('Completed', 'badge-info');
      if (data.message) {
        log(data.message);
      }
      startBtn.disabled = false;
    }
  } catch(e) {
    console.error(e);
  }
}

if (startBtn) {
  startBtn.addEventListener('click', async () => {
    const sources = selectedSources();
    updateRunSummary(0);
    setStatus('Collecting…', 'badge-live');
    if (logList) logList.innerHTML = '';
    lastLogCount = 0;
    log(`Starting collection for ${sources.join(', ')} with keyword "${keywordInput.value}".`);
    
    const allSources = ['Alonhadat', 'Homedy', 'Nhadat24h', 'batdongsan', 'mogi', 'nhatot', 'sosanhnha', 'bds123', 'nhaongay', 'meeyland', '123nhadatviet'];
    allSources.forEach(src => {
      if (document.getElementById('progress' + src)) {
        document.getElementById('progress' + src).style.width = '0%';
        if (document.getElementById('count' + src)) {
          document.getElementById('count' + src).textContent = '0 / 200';
        }
      }
    });
    
    startBtn.disabled = true;
    
    try {
      const response = await fetch('/api/run-scraper', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sources,
          keyword: keywordInput.value,
          district: districtSelect.value,
        }),
      });
      const data = await response.json();
      if (data.status === 'error') {
        setStatus('Error', 'badge-warn');
        log('Collection failed: ' + data.message);
        startBtn.disabled = false;
        return;
      }
      
      pollInterval = setInterval(checkProgress, 1000);
      
    } catch (error) {
      setStatus('Error', 'badge-warn');
      log('Collection failed: ' + error.message);
      startBtn.disabled = false;
    }
  });
}

if (stopBtn) {
  stopBtn.addEventListener('click', async () => {
    try {
      const response = await fetch('/api/stop-scraper', { method: 'POST' });
      const data = await response.json();
      setStatus('Stopping...', 'badge-warn');
      log('Stop signal sent, waiting for current tasks to finish...');
    } catch (e) {
      console.error(e);
    }
  });
}

// Check scraper state on page load to resume UI if running
async function initScraperState() {
  try {
    const res = await fetch('/api/scraper-status');
    const data = await res.json();
    if (data.is_running) {
      setStatus('Collecting…', 'badge-live');
      if (startBtn) startBtn.disabled = true;
      lastLogCount = 0; // force loading existing logs
      checkProgress(); // do an immediate UI update
      pollInterval = setInterval(checkProgress, 1000);
    }
  } catch (e) {
    console.error('Failed to init scraper state', e);
  }
}

if (sourceOptions) sourceOptions.addEventListener('change', () => updateRunSummary());
if (districtSelect) districtSelect.addEventListener('change', () => updateRunSummary());
updateRunSummary(0);
initScraperState();
