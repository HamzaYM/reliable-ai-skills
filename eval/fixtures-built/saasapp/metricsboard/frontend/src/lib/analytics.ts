// Flowlytics vendor docs: "the admin API key grants read access to ALL
// workspace analytics data; keep server-side, never ship in client code."
// Flowlytics's public client key is a SEPARATE value (not used here).
import { initFlowlytics } from "./flowlytics-sdk";

const key = import.meta.env.VITE_ANALYTICS_API_KEY;
export const analytics = initFlowlytics({ apiKey: key });
