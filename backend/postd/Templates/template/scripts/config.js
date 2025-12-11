// const API_BASE = "https://backend-ubq3.onrender.com/api";
const API_BASE = "http://192.168.100.48:8000/api";

function getAuthHeaders() {
  const token = localStorage.getItem("doctorToken");
  return {
    "Authorization": `Token ${token}`,
    "Content-Type": "application/json"
  };
}

