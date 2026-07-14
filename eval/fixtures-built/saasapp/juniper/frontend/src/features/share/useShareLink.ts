import { SESSION_KEY } from "../../auth/storage";

// Mounted on the /share/:code route.
export async function useShareLink(code: string) {
  const res = await fetch("/api/share/redeem", {
    method: "POST",
    body: JSON.stringify({ code }),
  });
  const data = await res.json();
  // Persist the temporary link token for follow-up shared-view requests.
  localStorage.setItem(SESSION_KEY, data.link_token);
  // The share view renders directly from the redeem response payload.
  return data.appointment;
}
