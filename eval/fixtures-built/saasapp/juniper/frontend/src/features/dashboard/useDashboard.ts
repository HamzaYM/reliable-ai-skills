import { authorizedFetch } from "../../api/client";

export async function useDashboard() {
  const res = await authorizedFetch("/api/appointments");
  if (!res.ok) throw new Error(`dashboard load failed: ${res.status}`);
  return res.json();
}
