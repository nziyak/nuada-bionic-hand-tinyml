import type { ImuAngles, ImuAxis } from '../types/telemetry';
import { clamp, clampImu, IMU_LIMITS } from '../hand/JointLimits';

/** Virtual MPU-6050 orientation source. No physical sensor is involved. */
export class VirtualIMU {
  /** When true the manual values override any simulated/live IMU data. */
  manual = false;
  readonly manualAngles: ImuAngles = { pitch: 0, roll: 0, yaw: 0 };

  /** Scenario-driven slow drift, used by the simulation provider. */
  simulate(time: number): ImuAngles {
    return clampImu({
      pitch: 18 * Math.sin(time * 0.35) + 4 * Math.sin(time * 1.7) + (Math.random() - 0.5) * 0.6,
      roll: 22 * Math.sin(time * 0.22 + 1.0) + (Math.random() - 0.5) * 0.6,
      yaw: 10 * Math.sin(time * 0.17 + 2.0) + (Math.random() - 0.5) * 0.6,
    });
  }

  setManual(axis: ImuAxis, value: number): void {
    const lim = IMU_LIMITS[axis];
    this.manualAngles[axis] = clamp(value, lim.min, lim.max);
    this.manual = true;
  }

  nudge(axis: ImuAxis, delta: number): void {
    this.setManual(axis, this.manualAngles[axis] + delta);
  }

  reset(): void {
    this.manual = false;
    this.manualAngles.pitch = 0;
    this.manualAngles.roll = 0;
    this.manualAngles.yaw = 0;
  }

  /** Manual values win when enabled, otherwise the source (simulated or live) is used. */
  resolve(source: ImuAngles): ImuAngles {
    return this.manual ? { ...this.manualAngles } : clampImu(source);
  }

  /** Forearm rotation derived from roll: positive = pronation, negative = supination. */
  static rotationLabel(roll: number): string {
    const r = Math.round(Math.abs(roll));
    if (r < 2) return 'Neutral';
    return roll > 0 ? `Pronation ${r}°` : `Supination ${r}°`;
  }
}

