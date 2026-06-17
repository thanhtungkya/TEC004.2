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
let lastLogCount = 0;


async function checkProgress() {
  try {
    const res = await fetch('/api/scraper-status');
    const data = await res.json();
    
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
    const sources = Array.from(sourceOptions.querySelectorAll('input:checked')).map((box) => box.value);
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
