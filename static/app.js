const dropzone = document.getElementById('dropzone');
const log = document.getElementById('log');
const toggle = document.getElementById('modeToggle');
const localLabel = document.getElementById('localLabel');
const remoteLabel = document.getElementById('remoteLabel');

function updateModeUI() {
  if (toggle.checked) {
    localLabel.classList.remove('active');
    remoteLabel.classList.add('active');
  } else {
    remoteLabel.classList.remove('active');
    localLabel.classList.add('active');
  }
}

toggle.addEventListener('change', updateModeUI);

['dragenter', 'dragover'].forEach(event => {
  dropzone.addEventListener(event, e => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });
});

['dragleave', 'drop'].forEach(event => {
  dropzone.addEventListener(event, e => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
  });
});

dropzone.addEventListener('drop', e => {
  const files = Array.from(e.dataTransfer.files);
  handleFiles(files);
});

dropzone.addEventListener('click', () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.multiple = true;
  input.accept = '.pdf';
  input.onchange = () => handleFiles(Array.from(input.files));
  input.click();
});

async function handleFiles(files) {
  if (!files.length) return;
  log.textContent += '[REMOTE] Appel API /api/scan/remote\n';
  const formData = new FormData();
  files.forEach(f => formData.append('files', f));

  try {
    const response = await fetch('/api/scan/remote', {
      method: 'POST',
      body: formData
    });
    const result = await response.json();
    log.textContent += `Réponse: ${JSON.stringify(result)}\n`;
  } catch (err) {
    log.textContent += `Erreur API: ${err}\n`;
  }
  
}
