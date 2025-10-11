const API_BASE =
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://backend-ubq3.onrender.com";


function getAuthHeaders() {
  const token = localStorage.getItem("doctorToken");
  return {
    "Authorization": `Token ${token}`,
    "Content-Type": "application/json"
  };
}

