// ===============================
// ELEMENTS DOM
// ===============================
const dropzone = document.getElementById('dropzone');
const log = document.getElementById('log');

const yaraRulesArea = document.getElementById('yaraRules');
const yaraNewArea = document.getElementById('yaraNew');
const yaraStatus = document.getElementById('yaraStatus');
const updateYaraBtn = document.getElementById('updateYaraBtn');

const tabs = document.querySelectorAll('.tab');
const contents = document.querySelectorAll('.tab-content');


// ===============================
// TAB NAVIGATION
// ===============================
tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    tabs.forEach(t => t.classList.remove('active'));
    contents.forEach(c => c.classList.remove('active'));

    tab.classList.add('active');
    document
      .getElementById(`tab-${tab.dataset.tab}`)
      .classList.add('active');
  });
});


// ===============================
// DRAG & DROP
// ===============================
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


// ===============================
// SCAN HANDLER (REMOTE)
// ===============================
async function handleFiles(files) {
  if (!files.length) return;

  // Afficher l'onglet scan si ce n'est pas le cas
  const scanTab = document.getElementById('tab-scan');
  if (!scanTab.classList.contains('active')) {
    tabs.forEach(t => t.classList.remove('active'));
    contents.forEach(c => c.classList.remove('active'));
    document.querySelector('[data-tab="scan"]').classList.add('active');
    scanTab.classList.add('active');
  }

  log.textContent += '\n[REMOTE] Appel API /api/scan/remote\n';

  const formData = new FormData();
  files.forEach(f => formData.append('files', f));

  try {
    const response = await fetch('/api/scan/remote', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();
    log.textContent += `Résultat:\n${JSON.stringify(result, null, 2)}\n`;
  } catch (err) {
    log.textContent += `❌ Erreur API: ${err.message}\n`;
  }
}


// ===============================
// YARA RULES MANAGEMENT
// ===============================
async function loadYaraRules() {
  try {
    const res = await fetch('/api/yara/rules');
    if (!res.ok) throw new Error('Erreur chargement règles');
    const data = await res.json();
    yaraRulesArea.value = data.rules;
  } catch (err) {
    yaraRulesArea.value = 'Erreur lors du chargement des règles YARA.';
  }
}

async function updateYaraRules() {
  const newRules = yaraNewArea.value.trim();
  if (!newRules) {
    yaraStatus.textContent = 'Aucune règle à ajouter.';
    return;
  }

  try {
    const res = await fetch('/api/yara/update', {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: newRules + '\n'
    });

    if (!res.ok) throw new Error('Erreur mise à jour');

    const data = await res.json();
    yaraStatus.textContent = data.status || 'Règles YARA mises à jour.';
    yaraNewArea.value = '';
    loadYaraRules();
  } catch (err) {
    yaraStatus.textContent = '❌ Erreur lors de la mise à jour des règles YARA.';
  }
}


// ===============================
// INIT
// ===============================
updateYaraBtn.addEventListener('click', updateYaraRules);
loadYaraRules();