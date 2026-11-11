import type { StatusLevel } from '../types/telemetry';

export interface DashboardView {
  gestureLabel: string;
  gestureDescription: string;
  gestureColor: string;
  phase: string;
  confidence: number;
  rotationLabel: string;
  statusText: string;
  statusLevel: StatusLevel;
  fps: number;
  latencyMs: number;
  dataAgeMs: number | null;
  packets: number;
  rejected: number;
}

/** Rolling FPS meter. */
export class FpsMeter {
  fps = 0;
  private frames = 0;
  private last = performance.now();

  tick(now: number): void {
    this.frames++;
    if (now - this.last >= 500) {
      this.fps = (this.frames * 1000) / (now - this.last);
      this.frames = 0;
      this.last = now;
    }
  }
}

function byId<T extends HTMLElement>(id: string): T {
  const el = document.getElementById(id);
  if (!el) throw new Error(`Missing element #${id}`);
  return el as T;
}

/** Read-only telemetry readouts. DOM writes are throttled to ~10 Hz. */
export class Dashboard {
  private readonly el = {
    badge: byId('status-badge'),
    state: byId('v-state'),
    fps: byId('v-fps'),
    latency: byId('v-latency'),
    age: byId('v-age'),
    packets: byId('v-packets'),
    invalid: byId('v-invalid'),
    gName: byId('g-name'),
    gPhase: byId('g-phase'),
    gConf: byId('g-conf'),
    gConfBar: byId('g-conf-bar'),
    bannerName: byId('banner-name'),
    bannerDesc: byId('banner-desc'),
    pronation: byId('v-pronation'),
  };
  private lastUpdate = 0;
  private lastColor = '';

  update(view: DashboardView, nowMs: number): void {
    if (nowMs - this.lastUpdate < 100) return;
    this.lastUpdate = nowMs;
    const e = this.el;

    e.badge.textContent = view.statusText;
    e.badge.className = `badge ${view.statusLevel}`;
    e.state.textContent = view.statusText;
    e.fps.textContent = view.fps.toFixed(0);
    e.latency.textContent = `${view.latencyMs.toFixed(0)} ms`;
    e.age.textContent = view.dataAgeMs === null ? '-' : `${view.dataAgeMs.toFixed(0)} ms`;
    e.packets.textContent = String(view.packets);
    e.invalid.textContent = String(view.rejected);

    e.gName.textContent = view.gestureLabel;
    e.gPhase.textContent = view.phase;
    e.gConf.textContent = `${Math.round(view.confidence * 100)}%`;
    e.gConfBar.style.width = `${Math.round(view.confidence * 100)}%`;
    e.bannerName.textContent = view.gestureLabel;
    e.bannerDesc.textContent = view.gestureDescription;
    e.pronation.textContent = view.rotationLabel;

    if (view.gestureColor !== this.lastColor) {
      this.lastColor = view.gestureColor;
      document.documentElement.style.setProperty('--accent', view.gestureColor);
    }
  }
}
