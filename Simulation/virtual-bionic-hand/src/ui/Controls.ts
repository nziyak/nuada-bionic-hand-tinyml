import {
  FINGER_IDS,
  GESTURE_IDS,
  type FingerId,
  type FingerValues,
  type GestureId,
  type ImuAngles,
  type ImuAxis,
} from '../types/telemetry';
import { FINGER_SPECS, IMU_LIMITS } from '../hand/JointLimits';
import { GESTURE_PROFILES } from '../hand/GestureController';

export interface ControlHandlers {
  onModeChange(mode: 'simulation' | 'live'): void;
  onAutoScenario(auto: boolean): void;
  onRandomScenario(random: boolean): void;
  onConnect(url: string): void;
  onDisconnect(): void;
  onGesture(g: GestureId): void;
  onManualFingers(enabled: boolean): void;
  onFinger(id: FingerId, flex: number): void;
  onManualImu(enabled: boolean): void;
  onImu(axis: ImuAxis, value: number): void;
  onImuNudge(axis: ImuAxis, delta: number): void;
  onImuReset(): void;
  onPause(): void;
  onResetHand(): void;
  onSafe(): void;
  onResetCamera(): void;
  onBadPacket(): void;
  onLoadModel(file: File): void;
  onResetModel(): void;
}

function byId<T extends HTMLElement>(id: string): T {
  const el = document.getElementById(id);
  if (!el) throw new Error(`Missing element #${id}`);
  return el as T;
}

interface SliderRow {
  input: HTMLInputElement;
  output: HTMLOutputElement;
  meta?: HTMLElement;
}

/** Builds and wires the manual control panel. */
export class Controls {
  private readonly gestureButtons = new Map<GestureId, HTMLButtonElement>();
  private readonly fingerRows = {} as Record<FingerId, SliderRow>;
  private readonly imuRows = {} as Record<ImuAxis, SliderRow>;
  private readonly manualFingers = byId<HTMLInputElement>('manual-fingers');
  private readonly manualImu = byId<HTMLInputElement>('manual-imu');
  private readonly pauseBtn = byId<HTMLButtonElement>('btn-pause');
  private readonly modeButtons = Array.from(document.querySelectorAll<HTMLButtonElement>('#mode-switch button'));
  private readonly wsConnect = byId<HTMLButtonElement>('ws-connect');
  private readonly wsStatus = byId('ws-status');
  private readonly wsUrl = byId<HTMLInputElement>('ws-url');
  private connected = false;
  private dragging: string | null = null;

  constructor(private readonly h: ControlHandlers) {
    this.buildGestureButtons();
    this.buildFingerRows();
    this.buildImuRows();
    this.bindStatic();
    this.bindKeyboard();
  }

  private buildGestureButtons(): void {
    const host = byId('gesture-buttons');
    for (const id of GESTURE_IDS) {
      const b = document.createElement('button');
      b.textContent = GESTURE_PROFILES[id].label;
      b.title = GESTURE_PROFILES[id].description;
      b.addEventListener('click', () => this.h.onGesture(id));
      host.appendChild(b);
      this.gestureButtons.set(id, b);
    }
  }

  private makeRow(host: HTMLElement, label: string, min: number, max: number, step: number, key: string, withMeta: boolean, onInput: (v: number) => void): SliderRow {
    const row = document.createElement('div');
    row.className = 'slider-row';
    const lab = document.createElement('label');
    lab.textContent = label;
    const input = document.createElement('input');
    input.type = 'range';
    input.min = String(min);
    input.max = String(max);
    input.step = String(step);
    input.value = '0';
    const output = document.createElement('output');
    output.textContent = '0';
    input.addEventListener('input', () => {
      this.dragging = key;
      onInput(Number(input.value));
    });
    const release = () => {
      if (this.dragging === key) this.dragging = null;
    };
    input.addEventListener('change', release);
    input.addEventListener('pointerup', release);
    row.append(lab, input, output);
    let meta: HTMLElement | undefined;
    if (withMeta) {
      meta = document.createElement('div');
      meta.className = 'finger-meta';
      row.appendChild(meta);
    }
    host.appendChild(row);
    return { input, output, meta };
  }

  private buildFingerRows(): void {
    const host = byId('finger-rows');
    for (const id of FINGER_IDS) {
      const spec = FINGER_SPECS[id];
      this.fingerRows[id] = this.makeRow(host, spec.label, 0, 100, 1, `f-${id}`, true, (v) => {
        this.setManualFingers(true);
        this.h.onFinger(id, v / 100);
      });
    }
  }

  private buildImuRows(): void {
    const host = byId('imu-rows');
    const labels: Record<ImuAxis, string> = { pitch: 'Pitch', roll: 'Roll', yaw: 'Yaw' };
    for (const axis of ['pitch', 'roll', 'yaw'] as const) {
      const lim = IMU_LIMITS[axis];
      this.imuRows[axis] = this.makeRow(host, labels[axis], lim.min, lim.max, 0.5, `i-${axis}`, false, (v) => {
        this.setManualImu(true);
        this.h.onImu(axis, v);
      });
    }
  }

  private bindStatic(): void {
    for (const b of this.modeButtons) {
      b.addEventListener('click', () => {
        const mode = b.dataset['mode'] === 'live' ? 'live' : 'simulation';
        this.setMode(mode);
        this.h.onModeChange(mode);
      });
    }
    byId<HTMLInputElement>('auto-scenario').addEventListener('change', (e) => this.h.onAutoScenario((e.target as HTMLInputElement).checked));
    byId<HTMLInputElement>('random-scenario').addEventListener('change', (e) => this.h.onRandomScenario((e.target as HTMLInputElement).checked));
    this.wsConnect.addEventListener('click', () => {
      if (this.connected) this.h.onDisconnect();
      else this.h.onConnect(this.wsUrl.value);
    });
    this.manualFingers.addEventListener('change', () => this.h.onManualFingers(this.manualFingers.checked));
    this.manualImu.addEventListener('change', () => this.h.onManualImu(this.manualImu.checked));
    byId('btn-imu-reset').addEventListener('click', () => this.h.onImuReset());
    this.pauseBtn.addEventListener('click', () => this.h.onPause());
    byId('btn-reset').addEventListener('click', () => this.h.onResetHand());
    byId('btn-safe').addEventListener('click', () => this.h.onSafe());
    byId('btn-camera').addEventListener('click', () => this.h.onResetCamera());
    byId('btn-bad').addEventListener('click', () => this.h.onBadPacket());
    byId('btn-model-reset').addEventListener('click', () => {
      this.setModelMessage('Using the built-in procedural model.');
      this.h.onResetModel();
    });
    byId<HTMLInputElement>('file-model').addEventListener('change', (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) this.h.onLoadModel(file);
    });
  }

  private bindKeyboard(): void {
    const keyMap: Record<string, [ImuAxis, number]> = {
      w: ['pitch', 3],
      s: ['pitch', -3],
      a: ['yaw', -3],
      d: ['yaw', 3],
      q: ['roll', -3],
      e: ['roll', 3],
    };
    window.addEventListener('keydown', (ev) => {
      const t = ev.target as HTMLElement | null;
      if (t && (t.tagName === 'INPUT' && (t as HTMLInputElement).type === 'text')) return;
      if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
      const k = ev.key.toLowerCase();
      if (k === ' ') {
        ev.preventDefault();
        this.h.onPause();
      } else if (k === 'r') {
        this.h.onImuReset();
      } else if (keyMap[k]) {
        const [axis, delta] = keyMap[k];
        this.setManualImu(true);
        this.h.onImuNudge(axis, delta);
      }
    });
  }

  // ─────────── state setters used by the app ───────────

  setMode(mode: 'simulation' | 'live'): void {
    for (const b of this.modeButtons) b.classList.toggle('active', b.dataset['mode'] === mode);
    byId('sim-options').classList.toggle('hidden', mode !== 'simulation');
    byId('live-options').classList.toggle('hidden', mode !== 'live');
  }

  setManualFingers(on: boolean): void {
    this.manualFingers.checked = on;
    this.h.onManualFingers(on);
  }

  setManualFingersSilent(on: boolean): void {
    this.manualFingers.checked = on;
  }

  setManualImu(on: boolean): void {
    if (this.manualImu.checked === on) return;
    this.manualImu.checked = on;
    this.h.onManualImu(on);
  }

  setManualImuSilent(on: boolean): void {
    this.manualImu.checked = on;
  }

  setAutoScenarioChecked(on: boolean): void {
    byId<HTMLInputElement>('auto-scenario').checked = on;
  }

  setPaused(paused: boolean): void {
    this.pauseBtn.textContent = paused ? 'Resume' : 'Pause';
    this.pauseBtn.classList.toggle('active', paused);
  }

  setActiveGesture(g: GestureId): void {
    for (const [id, b] of this.gestureButtons) b.classList.toggle('active', id === g);
  }

  setConnection(status: string, connected: boolean): void {
    this.connected = connected;
    this.wsStatus.textContent = status;
    this.wsConnect.textContent = connected ? 'Disconnect' : 'Connect';
  }

  setModelMessage(msg: string): void {
    byId('model-msg').textContent = msg;
  }

  /** Mirrors the live hand state into the sliders and readouts (without echoing events). */
  sync(flex: FingerValues, angles: FingerValues, imu: ImuAngles): void {
    for (const id of FINGER_IDS) {
      const row = this.fingerRows[id];
      if (this.dragging !== `f-${id}`) row.input.value = String(Math.round(flex[id] * 100));
      row.output.textContent = `${Math.round(flex[id] * 100)}%`;
      if (row.meta) row.meta.textContent = `Total joint angle ${angles[id].toFixed(0)}° (limit ${this.totalLimit(id)}°)`;
    }
    for (const axis of ['pitch', 'roll', 'yaw'] as const) {
      const row = this.imuRows[axis];
      if (this.dragging !== `i-${axis}`) row.input.value = String(imu[axis]);
      row.output.textContent = `${imu[axis].toFixed(1)}°`;
    }
  }

  private totalLimit(id: FingerId): number {
    return FINGER_SPECS[id].joints.reduce((s, j) => s + j.maxDeg, 0);
  }
}

