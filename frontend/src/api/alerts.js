import apiClient from "./client";

export async function getAlerts({ severity, status } = {}) {
  const params = {};
  if (severity) params.severity = severity;
  if (status) params.status = status;
  const response = await apiClient.get("/alerts/", { params });
  return response.data;
}

export async function investigateAlert(id) {
  const response = await apiClient.get(`/alerts/${id}/investigate`);
  return response.data;
}

export async function updateAlertStatus(id, status) {
  const response = await apiClient.patch(`/alerts/${id}/status`, { status });
  return response.data;
}