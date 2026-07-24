import apiClient from "./client";

export async function getLogs({ sourceIp, parsedOnly } = {}) {
  const params = {};
  if (sourceIp) params.source_ip = sourceIp;
  if (parsedOnly) params.parsed_only = true;

  const response = await apiClient.get("/logs/", { params });
  return response.data;
}