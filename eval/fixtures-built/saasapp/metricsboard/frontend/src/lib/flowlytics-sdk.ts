// Local stub of the Flowlytics browser SDK. The real SDK accepts either the
// public browser client key or the privileged admin/server key.
export function initFlowlytics(opts: { apiKey: string }) {
  return { track: (_e: string) => void _e, key: opts.apiKey };
}
