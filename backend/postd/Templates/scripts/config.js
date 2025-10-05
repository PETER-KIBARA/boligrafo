const API_BASE = "http://192.168.100.93:8000";

function getAuthHeaders() {
  const token = localStorage.getItem("doctorToken");
  return {
    "Authorization": `Token ${token}`,
    "Content-Type": "application/json"
  };
}

