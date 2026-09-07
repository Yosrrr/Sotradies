import apiClient from "./client";

export async function getRuntimeThresholds() {
  const { data } = await apiClient.get("/config/thresholds");
  return data;
}
export const getCategories = () => apiClient.get("/config/categories").then((r) => r.data);