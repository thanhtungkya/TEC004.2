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

let pollInterval = null;

async function checkProgress() {
  try {
    const res = await fetch('/api/scraper-status');
    const data = await res.json();
    
    if (data.progress) {
      if (document.getElementById('progressAlonhadat') && data.progress['alonhadat'] !== undefined) {
        document.getElementById('progressAlonhadat').style.width = Math.min(100, (data.progress['alonhadat']/200)*100) + '%';
        if (document.getElementById('countAlonhadat')) document.getElementById('countAlonhadat').textContent = data.progress['alonhadat'] + ' / 200';
      }
      if (document.getElementById('progressHomedy') && data.progress['homedy'] !== undefined) {
        document.getElementById('progressHomedy').style.width = Math.min(100, (data.progress['homedy']/200)*100) + '%';
        if (document.getElementById('countHomedy')) document.getElementById('countHomedy').textContent = data.progress['homedy'] + ' / 200';
      }
      if (document.getElementById('progressNhadat24h') && data.progress['nhadat24h'] !== undefined) {
        document.getElementById('progressNhadat24h').style.width = Math.min(100, (data.progress['nhadat24h']/200)*100) + '%';
        if (document.getElementById('countNhadat24h')) document.getElementById('countNhadat24h').textContent = data.progress['nhadat24h'] + ' / 200';
      }
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
    const sources = Array.from(sourceOptions.querySelectorAll('input:checked')).map((box) => box.value);
    setStatus('Collecting…', 'badge-live');
    log(`Starting collection for ${sources.join(', ')} with keyword "${keywordInput.value}".`);
    
    if (document.getElementById('progressAlonhadat')) { document.getElementById('progressAlonhadat').style.width = '0%'; if (document.getElementById('countAlonhadat')) document.getElementById('countAlonhadat').textContent = '0 / 200'; }
    if (document.getElementById('progressHomedy')) { document.getElementById('progressHomedy').style.width = '0%'; if (document.getElementById('countHomedy')) document.getElementById('countHomedy').textContent = '0 / 200'; }
    if (document.getElementById('progressNhadat24h')) { document.getElementById('progressNhadat24h').style.width = '0%'; if (document.getElementById('countNhadat24h')) document.getElementById('countNhadat24h').textContent = '0 / 200'; }
    
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
