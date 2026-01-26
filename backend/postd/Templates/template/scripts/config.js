// const API_BASE = "https://backend-ubq3.onrender.com/api";
const API_BASE = "http://192.168.100.159:8000/api";

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
