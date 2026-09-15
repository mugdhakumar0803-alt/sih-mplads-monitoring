const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("mplads_token");
  const isFormData = options.body instanceof FormData;
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `API error: ${response.status}`);
  }

  return response.json();
}

export async function checkBackend() {
  return apiRequest("/health");
}

export function loginRequest(username, password) {
  return apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function getCurrentUser() {
  return apiRequest("/auth/me");
}

export function getWorks(params = "") {
  return apiRequest(`/works/${params}`);
}

export function getWork(workId) {
  return apiRequest(`/works/${encodeURIComponent(workId)}`);
}

export function getGrievances(workId = "") {
  const query = workId ? `?work_id=${encodeURIComponent(workId)}` : "";
  return apiRequest(`/grievances/${query}`);
}

export function fileGrievance(data) {
  return apiRequest("/grievances/file", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function verifyPhoto(workId, file, captureDate) {
  const body = new FormData();
  body.append("work_id", workId);
  body.append("photo", file);
  if (captureDate) body.append("capture_date", captureDate);
  return apiRequest("/photos/verify", { method: "POST", body });
}

export function getPhotos(workId) {
  return apiRequest(`/photos/${encodeURIComponent(workId)}`);
}

export function getFundEligibility(workId) {
  return apiRequest(`/fund-release/eligibility/${encodeURIComponent(workId)}`);
}

export function getLeaderboard(
  level = "national",
  state = "",
  constituency = "",
) {
  const params = new URLSearchParams();

  params.set("level", level);

  if (state) {
    params.set("state", state);
  }

  if (constituency) {
    params.set("constituency", constituency);
  }

  return apiRequest(`/ratings/leaderboard?${params.toString()}`);
}
