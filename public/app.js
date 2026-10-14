const API = '/api/opportunities';

const listEl = document.getElementById('list');
const countLabel = document.getElementById('countLabel');
const alertBox = document.getElementById('alertBox');
const form = document.getElementById('oppForm');

const formModal = new bootstrap.Modal(document.getElementById('formModal'));
const detailModal = new bootstrap.Modal(document.getElementById('detailModal'));
const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));

const FIELDS = ['title', 'description', 'research_area', 'faculty_name',
                'department', 'required_skills', 'positions', 'deadline', 'status'];

let opportunities = [];
let pendingDeleteId = null;

// ---------- helpers ----------
function esc(text) {
  const div = document.createElement('div');
  div.textContent = text ?? '';
  return div.innerHTML;
}

function showMessage(type, text) {
  alertBox.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${esc(text)}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Wrapper around fetch: throws an Error with the server's message on non-2xx.
async function api(url, options = {}) {
  let res;
  try {
    res = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
  } catch (e) {
    throw new Error('Cannot reach the server. Is the backend running?');
  }
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const details = body.errors ? ': ' + body.errors.join('; ') : '';
    throw new Error((body.message || `Request failed (${res.status})`) + details);
  }
  return body;
}

// ---------- list ----------
async function loadList() {
  try {
    opportunities = await api(API);
    renderList();
  } catch (e) {
    listEl.innerHTML = '';
    showMessage('danger', e.message);
  }
}

function renderList() {
  countLabel.textContent = `${opportunities.length} opportunit${opportunities.length === 1 ? 'y' : 'ies'}`;
  if (!opportunities.length) {
    listEl.innerHTML = '<div class="col-12"><div class="alert alert-info">No opportunities yet. Click "New Opportunity" to add one.</div></div>';
    return;
  }
  listEl.innerHTML = opportunities.map(o => `
    <div class="col-md-6 col-lg-4">
      <div class="card h-100 shadow-sm">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h5 class="card-title mb-0">${esc(o.title)}</h5>
            <span class="badge ${o.status === 'Open' ? 'bg-success' : 'bg-secondary'}">${esc(o.status)}</span>
          </div>
          <p class="mb-1 text-muted small">${esc(o.research_area)} &middot; ${esc(o.department)}</p>
          <p class="mb-1 small"><strong>Faculty:</strong> ${esc(o.faculty_name)}</p>
          <p class="mb-1 small"><strong>Positions:</strong> ${o.positions}</p>
          <p class="mb-0 small"><strong>Deadline:</strong> ${esc(o.deadline)}</p>
        </div>
        <div class="card-footer bg-white d-flex flex-wrap gap-1">
          <button class="btn btn-sm btn-outline-primary" onclick="viewOne(${o.id})">View</button>
          <button class="btn btn-sm btn-outline-secondary" onclick="openEdit(${o.id})">Edit</button>
          ${o.status === 'Open'
            ? `<button class="btn btn-sm btn-outline-warning" onclick="closeOpportunity(${o.id})">Close</button>`
            : ''}
          <button class="btn btn-sm btn-outline-danger" onclick="askDelete(${o.id})">Delete</button>
        </div>
      </div>
    </div>`).join('');
}

// ---------- view one (fetched from the API by ID) ----------
async function viewOne(id) {
  try {
    const o = await api(`${API}/${id}`);
    document.getElementById('detailTitle').textContent = o.title;
    document.getElementById('detailBody').innerHTML = `
      <p><span class="badge ${o.status === 'Open' ? 'bg-success' : 'bg-secondary'}">${esc(o.status)}</span></p>
      <p>${esc(o.description).replace(/\n/g, '<br>')}</p>
      <table class="table table-sm">
        <tr><th style="width:35%">ID</th><td>${o.id}</td></tr>
        <tr><th>Research area</th><td>${esc(o.research_area)}</td></tr>
        <tr><th>Faculty member</th><td>${esc(o.faculty_name)}</td></tr>
        <tr><th>Department</th><td>${esc(o.department)}</td></tr>
        <tr><th>Required skills</th><td>${esc(o.required_skills)}</td></tr>
        <tr><th>Available positions</th><td>${o.positions}</td></tr>
        <tr><th>Application deadline</th><td>${esc(o.deadline)}</td></tr>
      </table>`;
    detailModal.show();
  } catch (e) {
    showMessage('danger', e.message);
    loadList(); // the item may have been deleted elsewhere
  }
}

// ---------- create / update ----------
document.getElementById('btnNew').addEventListener('click', () => {
  form.reset();
  form.classList.remove('was-validated');
  document.getElementById('oppId').value = '';
  document.getElementById('formTitle').textContent = 'New Research Opportunity';
  formModal.show();
});

async function openEdit(id) {
  try {
    const o = await api(`${API}/${id}`);
    form.classList.remove('was-validated');
    document.getElementById('oppId').value = o.id;
    FIELDS.forEach(f => { document.getElementById(f).value = o[f]; });
    document.getElementById('formTitle').textContent = `Edit Opportunity #${o.id}`;
    formModal.show();
  } catch (e) {
    showMessage('danger', e.message);
    loadList();
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  form.classList.add('was-validated'); // basic client-side validation
  if (!form.checkValidity()) return;

  const payload = {};
  FIELDS.forEach(f => { payload[f] = document.getElementById(f).value.trim(); });
  payload.positions = Number(payload.positions);

  const id = document.getElementById('oppId').value;
  try {
    if (id) {
      await api(`${API}/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
      showMessage('success', 'Opportunity updated successfully.');
    } else {
      await api(API, { method: 'POST', body: JSON.stringify(payload) });
      showMessage('success', 'Opportunity created successfully.');
    }
    formModal.hide();
    loadList();
  } catch (e) {
    showMessage('danger', e.message);
  }
});

// ---------- close (Open -> Closed) ----------
async function closeOpportunity(id) {
  try {
    await api(`${API}/${id}`, { method: 'PUT', body: JSON.stringify({ status: 'Closed' }) });
    showMessage('success', 'Opportunity closed.');
    loadList();
  } catch (e) {
    showMessage('danger', e.message);
    loadList();
  }
}

// ---------- delete ----------
function askDelete(id) {
  const o = opportunities.find(x => x.id === id);
  pendingDeleteId = id;
  document.getElementById('deleteBody').textContent =
    `Are you sure you want to delete "${o ? o.title : '#' + id}"? This cannot be undone.`;
  deleteModal.show();
}

document.getElementById('btnConfirmDelete').addEventListener('click', async () => {
  try {
    await api(`${API}/${pendingDeleteId}`, { method: 'DELETE' });
    showMessage('success', 'Opportunity deleted.');
  } catch (e) {
    showMessage('danger', e.message);
  }
  deleteModal.hide();
  loadList();
});

loadList();
