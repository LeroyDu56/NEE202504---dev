const API_BASE = 'http://192.168.200.152:8765';   // ton API
const SOURCE   = 'web.vue-app';

export function logClient(message, extra = {}) {
  const ev = {
    Ts: new Date().toISOString(),
    Source: SOURCE,
    RequestId: extra.RequestId || sessionId,
    Message: String(message),
    CodeLog: extra.CodeLog,
    UserId: extra.UserId
  };
  fetch(`${API_BASE}/logs/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ events: [ev] }),
    keepalive: true   // utile lors des changements de page
  }).catch(() => {});
}
