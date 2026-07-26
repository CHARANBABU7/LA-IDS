import apiClient from "./client";

export async function uploadLogFile(file, logType) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("log_type", logType);

  const response = await apiClient.post("/logs/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function runDetection() {
  const response = await apiClient.post("/detect/run");
  return response.data;
}