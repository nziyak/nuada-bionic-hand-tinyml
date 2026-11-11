import './style.css';
import { SceneManager } from './scene/SceneManager';
import { VirtualHand } from './hand/VirtualHand';
import { GESTURE_PROFILES, GestureController } from './hand/GestureController';
import { REST_FINGERS } from './hand/JointLimits';
import { SimulationDataProvider } from './data/SimulationDataProvider';
import { WebSocketClient } from './data/WebSocketClient';
import { parseTelemetry } from './data/DataParser';
import { VirtualEMG } from './sensors/VirtualEMG';
import { VirtualIMU } from './sensors/VirtualIMU';
import { Dashboard, FpsMeter } from './ui/Dashboard';
import { EmgChart } from './ui/Charts';
import { Controls } from './ui/Controls';
import {
  FINGER_IDS,
  type DataMode,
  type EmgFrame,
  type FingerValues,
  type ImuAngles,
  type StatusLevel,
  type Telemetry,
} from './types/telemetry';

/** If no valid packet arrives for this long in Live Data Mode, the hand goes to the safe Rest pose. */
const STALE_MS = 1000;
/** After an injected/invalid fault the stream is ignored for a moment so the safe reaction is visible. */
const FAULT_HOLD_MS = 1500;

const BAD_PACKETS = [
  '{"gesture":"fist","confidence":0.9',
  '{"gesture":"pinch","confidence":0.9,"thumb":9.5,"index":0.2,"middle":0.1}',
  '{"gesture":"banana","confidence":0.8}',
  '{"gesture":"open","confidence":"high","emg":[1,2]}',
];

class App {
  private readonly sceneManager: SceneManager;
  private readonly hand = new VirtualHand();
  private readonly gestures = new GestureController();
  private readonly emg = new VirtualEMG();
  private readonly imu = new VirtualIMU();
  private readonly sim = new SimulationDataProvider(this.emg, this.imu);
  private readonly ws = new WebSocketClient();
  private readonly dashboard = new Dashboard();
  private readonly fpsMeter = new FpsMeter();
  private readonly chart: EmgChart;
  private readonly controls: Controls;

  private mode: DataMode = 'simulation';
  private paused = false;
  private safeHold = false;
  private manualFingers = false;
  private readonly manualFlex: FingerValues = { ...REST_FINGERS };

  private latest: Telemetry | null = null;
  private lastPacketAt = 0;
  private faultUntil = 0;
  private packets = 0;
  private rejected = 0;
  private badIndex = 0;
  private latencyMs = 0;
  private lastClock = performance.now();
  private lastSync = 0;
  private readonly emgDisplay: EmgFrame = [0, 0, 0, 0];
  private readonly imuDisplay: ImuAngles = { pitch: 0, roll: 0, yaw: 0 };

  constructor() {
    const viewport = document.getElementById('viewport');
    const emgCanvas = document.getElementById('emg-canvas');
    const legend = document.getElementById('emg-legend');
    if (!viewport || !(emgCanvas instanceof HTMLCanvasElement) || !legend) throw new Error('Page structure is broken');

    this.sceneManager = new SceneManager(viewport);
    this.sceneManager.add(this.hand.root);
    this.chart = new EmgChart(emgCanvas, legend);

    this.controls = new Controls({
      onModeChange: (m) => this.setMode(m),
      onAutoScenario: (a) => this.sim.setAuto(a),
      onRandomScenario: (r) => (this.sim.random = r),
      onConnect: (url) => this.ws.connect(url),
      onDisconnect: () => this.ws.disconnect(),
      onGesture: (g) => this.selectGesture(g),
      onManualFingers: (on) => this.setManualFingers(on),
      onFinger: (id, v) => (this.manualFlex[id] = v),
      onManualImu: (on) => {
        this.imu.manual = on;
        if (on) Object.assign(this.imu.manualAngles, this.imuDisplay);
      },
      onImu: (axis, v) => this.imu.setManual(axis, v),
      onImuNudge: (axis, d) => {
        if (!this.imu.manual) Object.assign(this.imu.manualAngles, this.imuDisplay);
        this.imu.nudge(axis, d);
      },
      onImuReset: () => {
        this.imu.reset();
        this.controls.setManualImuSilent(false);
      },
      onPause: () => this.togglePause(),
      onResetHand: () => this.resetHand(),
      onSafe: () => this.enterSafeHold(),
      onResetCamera: () => this.sceneManager.cameraManager.reset(),
      onBadPacket: () => this.injectBadPacket(),
      onLoadModel: (file) => void this.loadModel(file),
      onResetModel: () => this.hand.resetModel(),
    });

    this.sim.onTelemetry = (t) => this.handleTelemetry(t);
    this.ws.onTelemetry = (t) => this.handleTelemetry(t);
    this.ws.onInvalid = (reason) => this.handleInvalid(reason);
    this.ws.onStatus = (status, detail) => this.controls.setConnection(detail, status === 'open' || status === 'connecting');

    this.gestures.enterSafe('Waiting for data');
    this.controls.setMode('simulation');
    this.controls.setPaused(false);

    const modelUrl = new URLSearchParams(location.search).get('model');
    if (modelUrl) void this.loadModel(modelUrl);

    this.sceneManager.renderer.setAnimationLoop(this.frame);
  }

  // ───────────── data handling ─────────────

  private handleTelemetry(t: Telemetry): void {
    const now = performance.now();
    if (this.paused || this.safeHold || now < this.faultUntil) return;
    this.lastPacketAt = now;
    this.packets++;
    this.latest = t;
    this.latencyMs += (t.inferenceLatencyMs - this.latencyMs) * 0.2;
    this.gestures.ingest(t, now);
    this.chart.push(t.emg);
  }

  private handleInvalid(reason: string): void {
    this.rejected++;
    console.warn('Rejected telemetry:', reason);
    if (this.paused || this.safeHold) return;
    this.gestures.enterSafe('Invalid data');
    this.faultUntil = performance.now() + FAULT_HOLD_MS;
  }

  private injectBadPacket(): void {
    const result = parseTelemetry(BAD_PACKETS[this.badIndex++ % BAD_PACKETS.length]);
    if (!result.ok) this.handleInvalid(result.reason);
  }

  // ───────────── user actions ─────────────

  private setMode(mode: DataMode): void {
    this.mode = mode;
    this.safeHold = false;
    this.latest = null;
    this.lastPacketAt = performance.now();
    if (mode === 'simulation') {
      this.ws.disconnect();
    } else {
      this.gestures.enterSafe('No data');
    }
  }

  private selectGesture(g: Telemetry['gesture']): void {
    this.safeHold = false;
    this.faultUntil = 0;
    this.manualFingers = false;
    this.controls.setManualFingersSilent(false);
    this.gestures.forceGesture(g);
    if (this.mode === 'simulation') {
      this.sim.setAuto(false);
      this.sim.setGesture(g);
      this.controls.setAutoScenarioChecked(false);
    }
  }

  private setManualFingers(on: boolean): void {
    if (on && !this.manualFingers) {
      for (const f of FINGER_IDS) this.manualFlex[f] = this.hand.fingers[f].value;
    }
    this.manualFingers = on;
  }

  private togglePause(): void {
    this.paused = !this.paused;
    this.lastPacketAt = performance.now();
    this.controls.setPaused(this.paused);
  }

  private resetHand(): void {
    this.safeHold = false;
    this.faultUntil = 0;
    this.manualFingers = false;
    this.controls.setManualFingersSilent(false);
    this.imu.reset();
    this.controls.setManualImuSilent(false);
    this.gestures.forceGesture('rest');
    this.hand.snapReset(REST_FINGERS);
    if (this.mode === 'simulation') {
      this.sim.restart();
      this.controls.setAutoScenarioChecked(true);
    }
  }

  private enterSafeHold(): void {
    this.safeHold = true;
    this.manualFingers = false;
    this.controls.setManualFingersSilent(false);
    this.gestures.enterSafe('Operator safe position');
  }

  private async loadModel(source: File | string): Promise<void> {
    this.controls.setModelMessage('Loading model…');
    const result = await this.hand.loadModel(source);
    this.controls.setModelMessage(result.message);
  }

  // ───────────── main loop ─────────────

  private readonly frame = (): void => {
    const now = performance.now();
    const dt = Math.min((now - this.lastClock) / 1000, 0.05);
    this.lastClock = now;

    if (this.mode === 'simulation' && !this.paused && !this.safeHold) this.sim.update(dt);

    // Watchdog: a dead or stalled stream puts the hand in the safe Rest pose.
    if (this.mode === 'live' && !this.paused && !this.safeHold && this.gestures.phase !== 'safe' && now - this.lastPacketAt > STALE_MS) {
      this.gestures.enterSafe('Stale data');
    }

    const safe = this.safeHold || this.gestures.phase === 'safe';

    // IMU → orientation (slerp inside VirtualHand).
    const imuSource: ImuAngles = this.latest && !safe ? this.latest.imu : { pitch: 0, roll: 0, yaw: 0 };
    const imuAngles = this.safeHold ? { pitch: 0, roll: 0, yaw: 0 } : this.imu.resolve(imuSource);
    this.imuDisplay.pitch = imuAngles.pitch;
    this.imuDisplay.roll = imuAngles.roll;
    this.imuDisplay.yaw = imuAngles.yaw;
    this.hand.setOrientation(imuAngles, dt);

    // Fingers.
    if (this.manualFingers && !this.safeHold) this.hand.setFingerTargets(this.manualFlex, 1);
    else this.hand.setFingerTargets(this.gestures.targets, this.gestures.speedScale);

    const profile = GESTURE_PROFILES[this.gestures.current];
    this.hand.setAccent(profile.color);
    const emgTarget: EmgFrame = this.latest && !safe ? this.latest.emg : [0, 0, 0, 0];
    const k = 1 - Math.exp(-10 * dt);
    for (let i = 0; i < 4; i++) this.emgDisplay[i] += (emgTarget[i] - this.emgDisplay[i]) * k;
    this.hand.setEmg(this.emgDisplay);
    this.hand.update(dt);
    this.gestures.update(this.hand.settled);

    this.sceneManager.update(dt);
    this.sceneManager.render();

    this.fpsMeter.tick(now);
    this.chart.draw(now);
    this.updateUi(now, profile.id);
  };

  private updateUi(now: number, gestureId: Telemetry['gesture']): void {
    const status = this.computeStatus();
    const profile = GESTURE_PROFILES[gestureId];
    this.dashboard.update(
      {
        gestureLabel: profile.label,
        gestureDescription: profile.description,
        gestureColor: `#${profile.color.toString(16).padStart(6, '0')}`,
        phase: this.gestures.phase,
        confidence: this.gestures.confidence,
        rotationLabel: VirtualIMU.rotationLabel(this.imuDisplay.roll),
        statusText: status.text,
        statusLevel: status.level,
        fps: this.fpsMeter.fps,
        latencyMs: this.latencyMs,
        dataAgeMs: this.packets > 0 ? now - this.lastPacketAt : null,
        packets: this.packets,
        rejected: this.rejected,
      },
      now,
    );

    if (now - this.lastSync > 60) {
      this.lastSync = now;
      const flex: FingerValues = { thumb: 0, index: 0, middle: 0 };
      const angles: FingerValues = { thumb: 0, index: 0, middle: 0 };
      for (const f of FINGER_IDS) {
        flex[f] = this.hand.fingers[f].value;
        angles[f] = this.hand.fingers[f].totalAngleDeg;
      }
      this.controls.sync(flex, angles, this.imuDisplay);
      this.controls.setActiveGesture(gestureId);
    }
  }

  private computeStatus(): { text: string; level: StatusLevel } {
    if (this.paused) return { text: 'PAUSED', level: 'warn' };
    if (this.safeHold) return { text: 'SAFE POSITION (HOLD)', level: 'warn' };
    if (this.gestures.phase === 'safe') {
      const invalid = this.gestures.safeReason === 'Invalid data';
      return { text: `SAFE · ${this.gestures.safeReason.toUpperCase()}`, level: invalid ? 'error' : 'warn' };
    }
    return this.mode === 'simulation'
      ? { text: this.sim.auto ? 'SIMULATING (SCENARIO)' : 'SIMULATING (MANUAL)', level: 'ok' }
      : { text: 'LIVE DATA', level: 'ok' };
  }
}

new App();

