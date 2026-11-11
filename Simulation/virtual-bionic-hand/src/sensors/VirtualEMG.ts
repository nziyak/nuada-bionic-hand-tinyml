import { GESTURE_IDS, type EmgFrame, type GestureId } from '../types/telemetry';
import { clamp } from '../hand/JointLimits';

/** Names of the four virtual sEMG channels (forearm muscle groups from the reference project). */
export const EMG_CHANNEL_NAMES = ['FDS', 'FPL', 'ED', 'EPL'] as const;

/** Target envelope per gesture: [FDS, FPL, ED, EPL]. */
const EMG_PROFILES: Record<GestureId, EmgFrame> = {
  rest: [0.05, 0.04, 0.05, 0.04],
  open_hand: [0.1, 0.08, 0.75, 0.6],
  power_grasp: [0.85, 0.7, 0.2, 0.15],
  fist: [0.95, 0.85, 0.15, 0.1],
  pinch_grasp: [0.45, 0.7, 0.1, 0.15],
  pointing: [0.5, 0.2, 0.65, 0.3],
  partial_grasp: [0.45, 0.4, 0.25, 0.2],
  thumb_index_contact: [0.4, 0.65, 0.15, 0.2],
  thumb_middle_contact: [0.55, 0.6, 0.15, 0.2],
};

/** Synthetic 4-channel sEMG envelope generator (no real sensor). */
export class VirtualEMG {
  readonly values: EmgFrame = [0.05, 0.04, 0.05, 0.04];

  /** Advance the envelope towards the gesture profile and add physiological-looking noise. */
  step(gesture: GestureId, dt: number, time: number): EmgFrame {
    const target = EMG_PROFILES[gesture];
    const a = 1 - Math.exp(-7 * dt);
    for (let i = 0; i < 4; i++) {
      this.values[i] += (target[i] - this.values[i]) * a;
      const noise =
        (Math.sin(time * (13 + i * 5.3) + i) * 0.5 + Math.random() - 0.5) * 0.06 * (0.3 + this.values[i]);
      this.values[i] = clamp(this.values[i] + noise * dt * 12, 0, 1);
    }
    return this.values;
  }

  static isKnown(g: string): g is GestureId {
    return (GESTURE_IDS as readonly string[]).includes(g);
  }
}

/** Blue (low) → red (high) colour for an activation value. */
export function emgHue(v: number): number {
  return 0.62 * (1 - clamp(v, 0, 1));
}

