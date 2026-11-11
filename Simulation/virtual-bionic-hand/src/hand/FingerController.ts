import { Object3D, Quaternion, Vector3 } from 'three';
import { clamp, jointAngleDeg, type FingerSpec } from './JointLimits';

const DEG2RAD = Math.PI / 180;

/**
 * Drives the joints of one finger. Each joint can be rotated independently;
 * flexion is smoothed with exponential easing and a speed limit, and the
 * resulting joint angles are always clamped to the virtual limits.
 */
export class FingerController {
  readonly spec: FingerSpec;
  /** Requested flexion (0..1). */
  target = 0;
  /** Current smoothed flexion (0..1). */
  value = 0;
  /** Flexion velocity (units/s), used for glow. */
  velocity = 0;
  /** Smoothed activity level (0..1) used for the glow effect. */
  glow = 0;
  /** Multiplies the finger speed limit (reduced for low-confidence data). */
  speedScale = 1;
  /** Joint angles in degrees after the last update. */
  readonly jointAngles: number[];

  private joints: Object3D[] = [];
  private restQuats: Quaternion[] = [];
  private readonly axes: Vector3[];
  private readonly tmpQ = new Quaternion();

  constructor(spec: FingerSpec, joints: Object3D[]) {
    this.spec = spec;
    this.jointAngles = spec.joints.map((j) => j.minDeg);
    this.axes = spec.joints.map((j) => new Vector3(...j.axis).normalize());
    this.bindJoints(joints);
  }

  /** (Re)bind to joint nodes, e.g. nodes of an imported GLB. Current local rotation is kept as rest pose. */
  bindJoints(joints: Object3D[]): void {
    this.joints = joints;
    this.restQuats = joints.map((j) => j.quaternion.clone());
  }

  setTarget(flex: number): void {
    this.target = clamp(Number.isFinite(flex) ? flex : 0, this.spec.minFlex, this.spec.maxFlex);
  }

  /** Jump to a value without animating (Reset). */
  snapTo(flex: number): void {
    this.setTarget(flex);
    this.value = this.target;
    this.velocity = 0;
    this.apply();
  }

  get totalAngleDeg(): number {
    let s = 0;
    for (const a of this.jointAngles) s += a;
    return s;
  }

  get settled(): boolean {
    return Math.abs(this.target - this.value) < 0.03;
  }

  update(dt: number, extraActivity = 0): void {
    if (dt <= 0) return;
    const alpha = 1 - Math.exp(-this.spec.smoothing * dt);
    const wanted = this.value + (this.target - this.value) * alpha;
    const maxStep = this.spec.maxSpeed * this.speedScale * dt;
    const delta = clamp(wanted - this.value, -maxStep, maxStep);
    this.value = clamp(this.value + delta, this.spec.minFlex, this.spec.maxFlex);
    this.velocity = delta / dt;

    const activity = clamp(this.value * 0.35 + Math.abs(this.velocity) * 0.6 + extraActivity * 0.4, 0, 1);
    this.glow += (activity - this.glow) * (1 - Math.exp(-8 * dt));
    this.apply();
  }

  private apply(): void {
    for (let i = 0; i < this.joints.length; i++) {
      const limit = this.spec.joints[i];
      const deg = jointAngleDeg(limit, this.value);
      this.jointAngles[i] = deg;
      this.tmpQ.setFromAxisAngle(this.axes[i], deg * DEG2RAD);
      this.joints[i].quaternion.copy(this.restQuats[i]).multiply(this.tmpQ);
    }
  }
}

