
function addRow() {
  const tasks = document.getElementById('tasks');
  const div = document.createElement('div');
  div.className = 'd-flex gap-2 align-items-center task-row';
  div.innerHTML = `
    <div class="task-autocomplete w-100">
      <input type="text" name="tasks[]" class="form-control task-input" placeholder="Task name" autocomplete="off">
      <div class="task-suggestions d-none"></div>
    </div>
    <div class="input-group" style="max-width: 160px;">
      <input type="number" name="percentages[]" class="form-control pct" min="0" max="100" step="0.01" placeholder="%">
      <span class="input-group-text">%</span>
    </div>
    <button class="btn btn-outline-secondary" type="button" onclick="removeRow(this)">Remove</button>
  `;
  tasks.appendChild(div);
  attachPctHandlers();
  setupAutocomplete(div.querySelector('.task-autocomplete'));
  // Distribute remaining percentage to the new row (and other unlocked rows)
  rebalancePercentages();
}

function removeRow(btn) {
  btn.closest('.task-row').remove();
  rebalancePercentages();
}

function getPctInputs() {
  return Array.from(document.querySelectorAll('#tasks input.pct'));
}

function round2(x) {
  return Math.round((Number(x) + Number.EPSILON) * 100) / 100;
}

function rebalancePercentages() {
  const inputs = getPctInputs();
  const n = inputs.length;
  if (n === 0) return;

  let lockedSum = 0;
  const unlockedInputs = [];

  // Identify locked vs unlocked inputs
  inputs.forEach(inp => {
    // Treat as locked if the user has manually edited it (dataset.locked)
    if (inp.dataset.locked === 'true') {
      const val = parseFloat(inp.value);
      lockedSum += (isNaN(val) ? 0 : val);
    } else {
      unlockedInputs.push(inp);
    }
  });

  const m = unlockedInputs.length;
  if (m === 0) return; // No unlocked inputs to balance

  // Calculate remainder to be distributed among unlocked inputs
  // We allow lockedSum to exceed 100 (user error preserved), in which case remainder is 0.
  const remainder = Math.max(0, 100 - lockedSum);

  // Distribute remainder evenly among unlocked inputs
  const even = remainder / m;
  let acc = 0;

  for (let i = 0; i < m - 1; i++) {
    const v = round2(even);
    unlockedInputs[i].value = v.toFixed(2);
    acc += v;
  }
  // Assign the rest to the last unlocked input to handle rounding errors
  const last = round2(remainder - acc);
  unlockedInputs[m - 1].value = last.toFixed(2);
}

function attachPctHandlers() {
  const inputs = getPctInputs();

  inputs.forEach((inp) => {
    if (inp.dataset.listenerAttached === 'true') return;

    // If the input already has a value (e.g. from server), mark it as locked
    if (inp.value !== '') {
      inp.dataset.locked = 'true';
    }

    const handler = () => {
      // If user clears the value, unlock it. If they enter a value, lock it.
      if (inp.value === '') {
        delete inp.dataset.locked;
      } else {
        inp.dataset.locked = 'true';
      }
      rebalancePercentages();
    };

    // Use 'change' to capture final edits. 
    inp.addEventListener('change', handler);
    // Also handle blur just in case
    inp.addEventListener('blur', handler);

    inp.dataset.listenerAttached = 'true';
  });
}

// Initialize handlers on page load
window.addEventListener('DOMContentLoaded', () => {
  attachPctHandlers();
  // Initialize autocomplete for existing rows
  document.querySelectorAll('.task-autocomplete').forEach(setupAutocomplete);
});

function setupAutocomplete(container) {
  const input = container.querySelector('input.task-input');
  const panel = container.querySelector('.task-suggestions');
  const dataEl = document.getElementById('task-options-data');
  const options = (dataEl?.dataset.options ? JSON.parse(dataEl.dataset.options) : []) || [];

  let filtered = [];
  let activeIndex = -1;
  let hideTimeout = null;

  function render() {
    panel.innerHTML = '';
    if (filtered.length === 0) {
      panel.classList.add('d-none');
      return;
    }
    const frag = document.createDocumentFragment();
    filtered.forEach((opt, idx) => {
      const item = document.createElement('div');
      item.className = 'task-suggestion-item' + (idx === activeIndex ? ' active' : '');
      item.textContent = opt;
      item.addEventListener('mousedown', (e) => {
        // use mousedown so the input doesn't lose focus before click
        e.preventDefault();
        choose(idx);
      });
      frag.appendChild(item);
    });
    panel.appendChild(frag);
    panel.classList.remove('d-none');
  }

  function choose(idx) {
    if (idx < 0 || idx >= filtered.length) return;
    input.value = filtered[idx];
    panel.classList.add('d-none');
  }

  function filter() {
    const q = (input.value || '').toLowerCase();
    // Exclude tasks already selected in other rows
    const selected = new Set(
      Array.from(document.querySelectorAll('.task-autocomplete input.task-input'))
        .filter(el => el !== input)
        .map(el => (el.value || '').trim())
        .filter(v => v !== '')
    );
    filtered = options
      .filter(o => !selected.has(o))
      .filter(o => o.toLowerCase().includes(q))
      .slice(0, 50);
    activeIndex = -1;
    render();
  }

  input.addEventListener('input', filter);
  input.addEventListener('change', filter);
  input.addEventListener('focus', () => {
    clearTimeout(hideTimeout);
    filter();
  });
  input.addEventListener('blur', () => {
    hideTimeout = setTimeout(() => panel.classList.add('d-none'), 150);
  });
  input.addEventListener('keydown', (e) => {
    if (panel.classList.contains('d-none')) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      activeIndex = Math.min(filtered.length - 1, activeIndex + 1);
      render();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      activeIndex = Math.max(0, activeIndex - 1);
      render();
    } else if (e.key === 'Enter') {
      if (activeIndex >= 0) {
        e.preventDefault();
        choose(activeIndex);
      }
    } else if (e.key === 'Escape') {
      panel.classList.add('d-none');
    }
  });
}
