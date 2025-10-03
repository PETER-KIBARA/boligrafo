const token = localStorage.getItem("doctorToken");

let currentPage = 1;
let currentQuery = "";

async function loadPatients() {
  const url = new URL(`${API_BASE}/list_patients`);
  url.searchParams.set("page", currentPage);
  if (currentQuery) url.searchParams.set("q", currentQuery);

  console.log("📡 Fetching:", url.toString());

  const res = await fetch(url, {
    headers: { Authorization: `Token ${token}` },
  });

  console.log("✅ Response status:", res.status);

  if (!res.ok) {
    console.error("❌ API request failed");
    return;
  }

  const data = await res.json();
  console.log("📦 API Response:", data);

  const tbody = document.querySelector("#patientsTable tbody");
  tbody.innerHTML = "";

  const patients = data.results || data;

  if (!patients.length) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No patients found</td></tr>`;
    return;
  }

  tbody.innerHTML = patients
    .map((p) => {
      const first = p.user ? p.user.first_name : p.first_name;
      const last = p.user ? p.user.last_name : p.last_name;
      const name = `${first || ""} ${last || ""}`.trim() || "-";

      const lastReading =
        p.last_reading && p.last_reading.systolic
          ? `<div class="reading">
              <strong>${p.last_reading.systolic}/${p.last_reading.diastolic} mmHg</strong>
              ${p.last_reading.heartrate ? `, ${p.last_reading.heartrate} bpm` : ""}
              <small>${p.last_reading.created_at}</small>
            </div>`
          : '<span class="text-muted">No readings</span>';

      return `<tr>
        <td>${name}</td>
        <td>${p.id}</td>
        <td>${p.phone || "-"}</td>
        <td>${lastReading}</td>
        <td class="text-end">
          <a class="btn btn-sm btn-primary" href="patient_profile.html?id=${p.id}">View</a>
        </td>
      </tr>`;
    })
    .join("");

  document.getElementById("pageInfo").textContent = data.count
    ? `Page ${currentPage}`
    : "";
  document.getElementById("prevBtn").disabled = currentPage <= 1;
  document.getElementById("nextBtn").disabled = !data.next;
}

document.getElementById("searchBtn").addEventListener("click", () => {
  currentQuery = document.getElementById("q").value.trim();
  currentPage = 1;
  loadPatients();
});

document.getElementById("prevBtn").addEventListener("click", () => {
  if (currentPage > 1) {
    currentPage--;
    loadPatients();
  }
});
document.getElementById("nextBtn").addEventListener("click", () => {
  currentPage++;
  loadPatients();
});

loadPatients();
