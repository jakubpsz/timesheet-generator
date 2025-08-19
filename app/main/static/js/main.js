
function addRow() {
  const tasks = document.getElementById('tasks');
  const div = document.createElement('div');
  div.className = 'd-flex gap-2 align-items-center task-row';
  div.innerHTML = `
    <input type="text" name="tasks[]" class="form-control" placeholder="Task name">
    <input type="number" name="percentages[]" class="form-control pct" min="0" max="100" step="0.01" placeholder="%">
    <button class="btn btn-outline-secondary" type="button" onclick="removeRow(this)">Remove</button>
  `;
  tasks.appendChild(div);
}
function removeRow(btn) {
  btn.closest('.task-row').remove();
}
