import { FINGER_IDS, GESTURE_IDS, type FingerValues, type GestureId, type Telemetry, type TelemetryListener } from '../types/telemetry';
import { GESTURE_PROFILES } from '../hand/GestureController';
import { clamp } from '../hand/JointLimits';
import type { VirtualEMG } from '../sensors/VirtualEMG';
import type { VirtualIMU } from '../sensors/VirtualIMU';

interface ScenarioStep {
  gesture: GestureId;
  duration: number;
}

const SCENARIO: ScenarioStep[] = [
  { gesture: 'rest', duration: 2.5 },
  { gesture: 'open_hand', duration: 2.5 },
  { gesture: 'power_grasp', duration: 3 },
  { gesture: 'open_hand', duration: 1.5 },
  { gesture: 'pinch_grasp', duration: 3 },
  { gesture: 'rest', duration: 1.5 },
  { gesture: 'pointing', duration: 3 },
  { gesture: 'partial_grasp', duration: 2.5 },
  { gesture: 'thumb_index_contact', duration: 3 },
  { gesture: 'thumb_middle_contact', duration: 3 },
  { gesture: 'fist', duration: 3 },
  { gesture: 'rest', duration: 2 },
];

const EMIT_INTERVAL = 1 / 50; // 50 Hz virtual telemetry

/**
 * Local, self-contained fake ESP32-S3 telemetry generator:
 * scenario or random gesture sequence, confidence, sEMG, IMU and TinyML latency.
 */
export class SimulationDataProvider {
  /** When false the gesture is held until `setGesture` is called again. */
  auto = true;
  random = false;
  onTelemetry: TelemetryListener = () => undefined;

  private gesture: GestureId = 'rest';
  private stepIndex = 0;
  private stepTime = 0;
  private sinceChange = 10;
  private time = 0;
  private accumulator = 0;
  private dipTimer = 6;
  private dipRemaining = 0;
  private randomDuration = 2;
  private readonly fingers: FingerValues = { ...GESTURE_PROFILES.rest.pose };

  constructor(
    private readonly emg: VirtualEMG,
    private readonly imu: VirtualIMU,
  ) {}

  get currentGesture(): GestureId {
    return this.gesture;
  }

  setGesture(g: GestureId): void {
    this.gesture = g;
    this.sinceChange = 0;
    this.stepTime = 0;
  }

  setAuto(auto: boolean): void {
    this.auto = auto;
    if (auto) this.setGesture(SCENARIO[this.stepIndex % SCENARIO.length].gesture);
  }

  restart(): void {
    this.stepIndex = 0;
    this.stepTime = 0;
    this.setGesture('rest');
    this.auto = true;
  }

  update(dt: number): void {
    this.time += dt;
    this.stepTime += dt;
    this.sinceChange += dt;

    if (this.auto) this.advanceScenario();

    this.dipTimer -= dt;
    if (this.dipTimer <= 0) {
      this.dipRemaining = 0.45;
      this.dipTimer = 7 + Math.random() * 5;
    }
    if (this.dipRemaining > 0) this.dipRemaining -= dt;

    this.accumulator += dt;
    let guard = 0;
    while (this.accumulator >= EMIT_INTERVAL && guard++ < 5) {
      this.accumulator -= EMIT_INTERVAL;
      this.onTelemetry(this.makePacket(EMIT_INTERVAL));
    }
    if (guard >= 5) this.accumulator = 0;
  }

  private advanceScenario(): void {
    if (this.random) {
      if (this.stepTime > this.randomDuration) {
        this.randomDuration = 1.5 + Math.random() * 2;
        this.setGesture(GESTURE_IDS[Math.floor(Math.random() * GESTURE_IDS.length)]);
      }
      return;
    }
    const step = SCENARIO[this.stepIndex % SCENARIO.length];
    if (this.stepTime >= step.duration) {
      this.stepIndex = (this.stepIndex + 1) % SCENARIO.length;
      this.setGesture(SCENARIO[this.stepIndex].gesture);
    }
  }

  private makePacket(dt: number): Telemetry {
    const pose = GESTURE_PROFILES[this.gesture].pose;
    for (const f of FINGER_IDS) {
      this.fingers[f] = clamp(pose[f] + (Math.random() - 0.5) * 0.03, 0, 1);
    }
    let confidence = 0.96 - 0.4 * Math.exp(-this.sinceChange / 0.25) + (Math.random() - 0.5) * 0.05;
    if (this.dipRemaining > 0) confidence = 0.28 + Math.random() * 0.12;
    confidence = clamp(confidence, 0, 1);

    const latency = 28 + Math.sin(this.time * 2.1) * 4 + Math.random() * 8 + (Math.random() < 0.02 ? 18 : 0);

    return {
      timestamp: Date.now(),
      gesture: this.gesture,
      confidence,
      fingers: { ...this.fingers },
      hasExplicitFingers: true,
      imu: this.imu.simulate(this.time),
      emg: [...this.emg.step(this.gesture, dt, this.time)] as Telemetry['emg'],
      inferenceLatencyMs: latency,
    };
  }
}
