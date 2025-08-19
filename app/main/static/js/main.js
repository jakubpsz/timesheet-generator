
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
  // Evenly distribute after adding a row
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

function rebalancePercentages(changedIndex = null) {
  const inputs = getPctInputs();
  const n = inputs.length;
  if (n === 0) return;

  // If no manual change triggered, evenly distribute to 100 with rounding fix
  if (changedIndex === null) {
    const even = 100 / n;
    let acc = 0;
    for (let i = 0; i < n - 1; i++) {
      const v = round2(even);
      inputs[i].value = v.toFixed(2);
      acc += v;
    }
    const last = round2(100 - acc);
    inputs[n - 1].value = last.toFixed(2);
    return;
  }

  // With a changed index, clamp so total stays at 100
  const changed = inputs[changedIndex];
  // Sum of rows above the changed one (they remain unchanged)
  let sumAbove = 0;
  for (let i = 0; i < changedIndex; i++) {
    sumAbove += parseFloat(inputs[i].value || '0') || 0;
  }
  let v = parseFloat(changed.value || '0');
  if (isNaN(v)) v = 0;
  // Clamp to [0, 100 - sumAbove]
  const maxAllowed = Math.max(0, 100 - sumAbove);
  v = Math.max(0, Math.min(maxAllowed, v));
  v = round2(v);
  changed.value = v.toFixed(2);

  const remainderTotal = round2(100 - (sumAbove + v));
  const remainder = Math.max(0, remainderTotal);

  // Recalculate only tasks BELOW the changed one
  const below = inputs.slice(changedIndex + 1);
  const m = below.length;
  if (m === 0) return;

  const currentSumBelow = below.reduce((s, el) => s + (parseFloat(el.value || '0') || 0), 0);
  if (currentSumBelow <= 0.000001) {
    // Spread remainder evenly with rounding fix on last
    const even = remainder / m;
    let acc = 0;
    for (let i = 0; i < m - 1; i++) {
      const val = round2(even);
      below[i].value = val.toFixed(2);
      acc += val;
    }
    const last = round2(remainder - acc);
    below[m - 1].value = last.toFixed(2);
  } else {
    // Scale proportionally to fit remainder, fix rounding on last
    let acc = 0;
    for (let i = 0; i < m - 1; i++) {
      const cur = parseFloat(below[i].value || '0') || 0;
      const scaled = round2(remainder * (cur / currentSumBelow));
      below[i].value = scaled.toFixed(2);
      acc += scaled;
    }
    const last = round2(remainder - acc);
    below[m - 1].value = last.toFixed(2);
  }
}

function attachPctHandlers() {
  // Evenly distribute on initial load if all blank
  const inputs = getPctInputs();
  if (inputs.length > 0 && inputs.every(inp => (inp.value ?? '') === '' || parseFloat(inp.value) === 0)) {
    rebalancePercentages();
  }

  inputs.forEach((inp) => {
    if (inp.dataset.listenerAttached === 'true') return;
    // Rebalance after editing is finished (on change/blur), not on every keystroke
    const handler = () => {
      const curIdx = getPctInputs().indexOf(inp);
      rebalancePercentages(curIdx);
    };
    inp.addEventListener('change', handler);
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
    filtered = options.filter(o => o.toLowerCase().includes(q)).slice(0, 50);
    activeIndex = -1;
    render();
  }

  input.addEventListener('input', filter);
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
