export const API_BASE = window.API_BASE || 'http://localhost:8000';

export function getAuthHeaders(){
  const token = localStorage.getItem('doctorToken');
  return { 'Content-Type': 'application/json', 'Authorization': `Token ${token ? token.replace(/"/g,'') : ''}` };
}

export async function authFetch(url, opts={}){
  opts.headers = Object.assign({}, getAuthHeaders(), opts.headers || {});
  return fetch(url, opts);
}