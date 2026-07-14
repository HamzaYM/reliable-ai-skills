import { SHARE_KEY } from "../auth/storage";

// Optional secondary path: refresh a shared view with the link token.
export async function shareFetch(path: string) {
  const token = localStorage.getItem(SHARE_KEY);
  return fetch(path, {
    headers: { Authorization: `Bearer ${token}` },
  });
}
