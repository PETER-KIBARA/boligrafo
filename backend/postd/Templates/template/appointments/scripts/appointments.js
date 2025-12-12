// appointments.js
// Exports a single module that handles fetching and UI for appointments.

import { API_BASE, getAuthHeaders, authFetch } from './_appointments_utils.js';

// We provide a small internal helper _appointments_utils.js inline below in README; if you already have
// scripts/config.js expose API_BASE and getAuthHeaders, you can remove the import and use global functions.

let deleteCandidateId = null;

async function fetchPatientsForSelect(sel) {
  try {
    const res = await authFetch(`${API_BASE}/list_patients`);
    if (!res.ok) throw new Error('Failed to load patients');
    const data = await res.json();
    const patients = Array.isArray(data) ? data : (data.results || []);
    sel.innerHTML = '<option value="">Select patient</option>' + patients.map(p => {
      const name = p.user ? `${p.user.first_name} ${p.user.last_name || ''}`.trim() : (p.first_name || 'Patient');
      // value using user id (patient.user.id) if available, otherwise patient.id
      const val = (p.user && p.user.id) ? p.user.id : p.id;
      return `<option value="${val}">${name} (ID: ${p.id})</option>`;
    }).join('');
  } catch (err) {
    console.error(err);
    sel.innerHTML = '<option value="">Unable to load patients</option>';
  }
}

async function loadAppointments() {
  const tbody = document.getElementById('appointmentsTable');
  tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4">Loading...</td></tr>';
  try {
    const res = await authFetch(`${API_BASE}/doctor/appointments`);
    if (!res.ok) throw new Error('Failed to fetch appointments');
    const data = await res.json();
    const list = Array.isArray(data) ? data : (data.results || []);
    if (!list.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">No appointments</td></tr>';
      return;
    }
    tbody.innerHTML = list.map(a => renderAppointmentRow(a)).join('');
    attachRowHandlers();
  } catch (err) {
    console.error(err);
    tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">Error loading appointments</td></tr>`;
  }
}

function renderAppointmentRow(a) {
  const date = new Date(a.date_time);
  const dateStr = date.toLocaleDateString();
  const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const statusBadge = statusToBadge(a.status);
  const patientName = a.patient_name || (a.patient && a.patient_name) || `Patient ${a.patient}`;

  return `
    <tr data-id="${a.id}">
      <td>${escapeHtml(patientName)}</td>
      <td>${a.patient || '-'}</td>
      <td>${dateStr}</td>
      <td>${timeStr}</td>
      <td>${escapeHtml(a.reason || '')}</td>
      <td>${statusBadge}</td>
      <td class="text-end">
        <a class="btn btn-sm btn-outline-primary me-1" href="appointment_view.html?id=${a.id}">View</a>
        <button class="btn btn-sm btn-danger btn-delete">Delete</button>
      </td>
    </tr>`;
}

function statusToBadge(s) {
  const st = (s || 'Pending').toLowerCase();
  if (st === 'pending') return '<span class="badge badge-status badge-pending">Pending</span>';
  if (st === 'confirmed') return '<span class="badge badge-status badge-confirmed">Confirmed</span>';
  if (st === 'completed') return '<span class="badge badge-status badge-completed">Completed</span>';
  if (st === 'cancelled') return '<span class="badge badge-status badge-cancelled">Cancelled</span>';
  return `<span class="badge badge-status">${escapeHtml(s)}</span>`;
}

function attachRowHandlers() {
  document.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const tr = e.target.closest('tr');
      deleteCandidateId = tr.dataset.id;
      const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
      modal.show();
    });
  });
}

async function confirmDelete() {
  if (!deleteCandidateId) return;
  try {
    const res = await fetch(`${API_BASE}/appointments/${deleteCandidateId}`, {
      method: 'DELETE', headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Delete failed');
    await loadAppointments();
    deleteCandidateId = null;
    bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal')).hide();
  } catch (err) {
    console.error(err);
    alert('Failed to delete appointment');
  }
}

function escapeHtml(str){
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Create appointment handler
async function handleCreate(e) {
  e.preventDefault();
  const patient = document.getElementById('patientSelect').value;
  const date = document.getElementById('apptDate').value;
  const time = document.getElementById('apptTime').value;
  const reason = document.getElementById('apptReason').value.trim();
  const notes = document.getElementById('apptNotes').value.trim();

  if (!patient || !date || !time || !reason) return alert('Please fill required fields');

  const dt = new Date(`${date}T${time}`);

  try {
    const res = await fetch(`${API_BASE}/appointments`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ patient: patient, date_time: dt.toISOString(), reason, notes })
    });
    if (!res.ok) throw new Error('Create failed');
    window.location.href = 'appointments.html';
  } catch (err) {
    console.error(err);
    alert('Failed to create appointment');
  }
}

// Appointment details page logic
async function loadAppointmentDetails() {
  const id = new URLSearchParams(location.search).get('id');
  if (!id) return;
  try {
    const res = await authFetch(`${API_BASE}/appointments/${id}`);
    if (!res.ok) throw new Error('Fetch failed');
    const a = await res.json();
    document.getElementById('detailPatientName').textContent = a.patient_name || `Patient ${a.patient}`;
    const date = new Date(a.date_time);
    document.getElementById('detailDatetime').textContent = date.toLocaleString();
    document.getElementById('detailReason').textContent = a.reason || '';
    document.getElementById('detailStatus').value = a.status || 'Pending';
    document.getElementById('detailNotes').value = a.notes || '';

    document.getElementById('saveDetailBtn').addEventListener('click', async ()=>{
      try {
        const payload = { status: document.getElementById('detailStatus').value, notes: document.getElementById('detailNotes').value };
        const upd = await fetch(`${API_BASE}/appointments/${id}`, { method: 'PATCH', headers: getAuthHeaders(), body: JSON.stringify(payload) });
        if (!upd.ok) throw new Error('Update failed');
        alert('Saved');
        location.reload();
      } catch(err){ console.error(err); alert('Failed to save'); }
    });

  } catch (err) { console.error(err); }
}

// Expose functions for module-pages
export async function initAppointmentsList() {
  document.getElementById('refreshBtn').addEventListener('click', loadAppointments);
  document.getElementById('appointmentSearch').addEventListener('input', (e)=>{ filterTable(e.target.value); });
  document.getElementById('statusFilter').addEventListener('change', ()=> { loadAppointments(); });
  document.getElementById('confirmDeleteBtn').addEventListener('click', confirmDelete);
  await loadAppointments();
}

export async function initCreatePage() {
  await fetchPatientsForSelect(document.getElementById('patientSelect'));
  document.getElementById('appointmentForm').addEventListener('submit', handleCreate);
}

export async function initDetailPage() {
  await loadAppointmentDetails();
}

function filterTable(q){
  q = (q||'').toLowerCase();
  document.querySelectorAll('#appointmentsTable tr').forEach(tr=>{
    const text = tr.textContent.toLowerCase();
    tr.style.display = text.includes(q) ? '' : 'none';
  });
}