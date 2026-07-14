import { SESSION_KEY } from "../auth/storage";

export async function authorizedFetch(path: string) {
  const token = localStorage.getItem(SESSION_KEY);
  return fetch(path, {
    headers: { Authorization: `Bearer ${token}` },
  });
}
