// const API_BASE = "https://undegrading-marcelo-euphemistical.ngrok-free.dev/api";
const API_BASE = "http://127.0.0.1:8000/api";

function getAuthHeaders() {
  const token = localStorage.getItem("doctorToken");
  return {
    "Authorization": `Token ${token}`,
    "Content-Type": "application/json"
  };
}

// Helper function for authenticated fetch requests
async function authFetch(url, options = {}) {
  const defaultOptions = {
    headers: getAuthHeaders(),
    ...options
  };
  return fetch(url, defaultOptions);
}
