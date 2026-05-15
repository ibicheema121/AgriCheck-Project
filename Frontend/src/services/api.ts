// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
//const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "") + "/api/v1";

interface RequestInit {
  method?: string;
  headers?: Record<string, string>;
  body?: string;
}

async function request<T>(endpoint: string, opts: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...opts.headers,
  };

  // Add Firebase token if available
  const token = localStorage.getItem("firebaseToken");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...opts,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// Helper functions
export const get = <T,>(endpoint: string) => 
  request<T>(endpoint, { method: "GET" });

export const post = <T,>(endpoint: string, body?: unknown) => 
  request<T>(endpoint, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });

export const put = <T,>(endpoint: string, body?: unknown) => 
  request<T>(endpoint, {
    method: "PUT",
    body: body ? JSON.stringify(body) : undefined,
  });

export const patch = <T,>(endpoint: string, body?: unknown) => 
  request<T>(endpoint, {
    method: "PATCH",
    body: body ? JSON.stringify(body) : undefined,
  });

export default { get, post, put, patch };
