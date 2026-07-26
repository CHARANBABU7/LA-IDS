import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

export async function checkHealth() {
  const response = await apiClient.get("/health");
  return response.data;
}

export default apiClient;