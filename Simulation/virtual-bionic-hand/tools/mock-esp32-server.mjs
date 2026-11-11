// Simulated ESP32-S3 telemetry stream for Live Data Mode.
// Pure software emulation: it only generates JSON text. No hardware is involved.
// Usage: npm run mock:ws   (optional: --port 8080  --corrupt)
import { WebSocketServer } from 'ws';

const args = process.argv.slice(2);
const portIdx = args.indexOf('--port');
const port = portIdx >= 0 ? Number(args[portIdx + 1]) : 8080;
const corrupt = args.includes('--corrupt');

const poses = {
  rest: [0.25, 0.2, 0.2],
  open: [0, 0, 0],
  power: [0.8, 0.85, 0.85],
  fist: [1, 1, 1],
  pinch: [0.45, 0.6, 0.2],
  pointing: [0.8, 0, 1],
  partial: [0.5, 0.5, 0.5],
  thumb_index: [0.45, 0.6, 0.05],
  thumb_middle: [0.65, 0.1, 0.7],
};
const emgProfiles = {
  rest: [0.05, 0.04, 0.05, 0.04],
  open: [0.1, 0.08, 0.75, 0.6],
  power: [0.85, 0.7, 0.2, 0.15],
  fist: [0.95, 0.85, 0.15, 0.1],
  pinch: [0.45, 0.7, 0.1, 0.15],
  pointing: [0.5, 0.2, 0.65, 0.3],
  partial: [0.45, 0.4, 0.25, 0.2],
  thumb_index: [0.4, 0.65, 0.15, 0.2],
  thumb_middle: [0.55, 0.6, 0.15, 0.2],
};
const names = Object.keys(poses);
const jitter = (s) => (Math.random() - 0.5) * s;
const clamp01 = (v) => Math.min(1, Math.max(0, v));

let gesture = 'rest';
let changedAt = Date.now();
setInterval(() => {
  gesture = names[Math.floor(Math.random() * names.length)];
  changedAt = Date.now();
}, 3000);

const wss = new WebSocketServer({ port });
console.log(`Mock telemetry server on ws://localhost:${port}${corrupt ? ' (with corrupt packets)' : ''}`);

setInterval(() => {
  const t = Date.now() / 1000;
  const since = (Date.now() - changedAt) / 1000;
  const p = poses[gesture];
  const msg = {
    timestamp: Math.floor(Date.now() / 1000),
    gesture,
    confidence: clamp01(0.95 - 0.4 * Math.exp(-since / 0.25) + jitter(0.04)),
    thumb: clamp01(p[0] + jitter(0.03)),
    index: clamp01(p[1] + jitter(0.03)),
    middle: clamp01(p[2] + jitter(0.03)),
    pitch: 18 * Math.sin(t * 0.4),
    roll: 20 * Math.sin(t * 0.25 + 1),
    yaw: 8 * Math.sin(t * 0.18),
    emg: emgProfiles[gesture].map((v) => clamp01(v + jitter(0.1))),
    inference_latency_ms: 28 + Math.random() * 10,
  };
  let text = JSON.stringify(msg);
  if (corrupt && Math.random() < 0.03) text = text.slice(0, text.length - 7);
  for (const client of wss.clients) if (client.readyState === 1) client.send(text);
}, 20);

