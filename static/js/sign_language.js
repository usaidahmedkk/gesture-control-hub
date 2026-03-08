/* Sign Language Interpreter — frontend logic */

const PROJECT = 'sign_language';
let polling = null;

function startProject() {
  fetch(`/start/${PROJECT}`, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        document.getElementById('placeholder').style.display = 'none';
        const feed = document.getElementById('feed');
        feed.src = `/video_feed/${PROJECT}`;
        feed.style.display = 'block';
        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('stopBtn').style.display = 'inline-block';
        document.getElementById('stopBtn2').style.display = 'inline-block';
        startPolling();
      } else {
        document.getElementById('statusBox') &&
          (document.getElementById('statusBox').textContent = 'Error: ' + (data.message || 'unknown'));
      }
    })
    .catch(() => {});
}

function stopProject() {
  fetch(`/stop/${PROJECT}`, { method: 'POST' });
  stopPolling();
  document.getElementById('feed').src = '';
  document.getElementById('feed').style.display = 'none';
  document.getElementById('placeholder').style.display = 'flex';
  document.getElementById('startBtn').style.display = 'inline-block';
  document.getElementById('stopBtn').style.display = 'none';
  document.getElementById('stopBtn2').style.display = 'none';
  document.getElementById('letterDisplay').textContent = '—';
  document.getElementById('confLabel').textContent = '—';
  document.getElementById('wordDisplay').innerHTML = '&nbsp;';
}

function stopAndBack() {
  fetch('/stop_all', { method: 'POST' }).finally(() => {
    location.href = '/';
  });
}

function sendAction(action) {
  fetch('/sign_language/action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  }).catch(() => {});
}

function startPolling() {
  polling = setInterval(() => {
    fetch(`/status/${PROJECT}`)
      .then(r => r.json())
      .then(data => {
        if (data.status === 'active') {
          document.getElementById('letterDisplay').textContent = data.letter || '—';
          document.getElementById('confLabel').textContent =
            data.confidence ? data.confidence + '%' : '—';
          const word = data.word || '';
          document.getElementById('wordDisplay').textContent = word || '\u00a0';
        }
      })
      .catch(() => {});
  }, 300);
}

function stopPolling() {
  if (polling) { clearInterval(polling); polling = null; }
}
