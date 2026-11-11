import { GESTURE_IDS, FINGER_IDS, type FingerValues, type GestureId, type GestureProfile, type Telemetry } from '../types/telemetry';
import { REST_FINGERS, clamp } from './JointLimits';

export const GESTURE_PROFILES: Record<GestureId, GestureProfile> = {
  rest: {
    id: 'rest',
    label: 'Rest',
    description: 'Relaxed neutral pose',
    color: 0x7aa2c9,
    pose: { ...REST_FINGERS },
  },
  open_hand: {
    id: 'open_hand',
    label: 'Open Hand',
    description: 'All fingers extended',
    color: 0x3ddc97,
    pose: { thumb: 0, index: 0, middle: 0 },
  },
  power_grasp: {
    id: 'power_grasp',
    label: 'Power Grasp',
    description: 'Strong closing around an object',
    color: 0xff8a3d,
    pose: { thumb: 0.8, index: 0.85, middle: 0.85 },
  },
  fist: {
    id: 'fist',
    label: 'Fist',
    description: 'Fully closed hand',
    color: 0xff4d6d,
    pose: { thumb: 1, index: 1, middle: 1 },
  },
  pinch_grasp: {
    id: 'pinch_grasp',
    label: 'Pinch Grasp',
    description: 'Precision grip with thumb and index',
    color: 0xb388ff,
    pose: { thumb: 0.45, index: 0.6, middle: 0.2 },
  },
  pointing: {
    id: 'pointing',
    label: 'Pointing',
    description: 'Index extended, others closed',
    color: 0x4dd0ff,
    pose: { thumb: 0.8, index: 0, middle: 1 },
  },
  partial_grasp: {
    id: 'partial_grasp',
    label: 'Partial Grasp',
    description: 'Half-closed hand',
    color: 0xffd23f,
    pose: { thumb: 0.5, index: 0.5, middle: 0.5 },
  },
  thumb_index_contact: {
    id: 'thumb_index_contact',
    label: 'Thumb-Index Contact',
    description: 'Thumb tip touches index tip',
    color: 0xf06ad8,
    pose: { thumb: 0.45, index: 0.6, middle: 0.05 },
  },
  thumb_middle_contact: {
    id: 'thumb_middle_contact',
    label: 'Thumb-Middle Contact',
    description: 'Thumb tip touches middle tip',
    color: 0x5eead4,
    pose: { thumb: 0.65, index: 0.1, middle: 0.7 },
  },
};

export type GesturePhase = 'holding' | 'transitioning' | 'safe';

const MIN_ACCEPT_CONFIDENCE = 0.45;
const DEBOUNCE_MS = 90;

function smoothstep(e0: number, e1: number, x: number): number {
  const t = clamp((x - e0) / (e1 - e0), 0, 1);
  return t * t * (3 - 2 * t);
}

/**
 * Gesture state machine.
 *
 *  holding ──(new gesture sustained, confident)──▶ transitioning ──(fingers settled)──▶ holding
 *  any ──(invalid data / stale stream / safe hold)──▶ safe (Rest pose) ──(valid packet)──▶ transitioning
 *
 * It also produces the finger targets: low-confidence packets only move the
 * targets partially (and slower), very low confidence is ignored (hold).
 */
export class GestureController {
  current: GestureId = 'rest';
  phase: GesturePhase = 'safe';
  confidence = 0;
  safeReason = 'Waiting for data';
  /** Smoothed, safety-filtered finger targets. */
  readonly targets: FingerValues = { ...REST_FINGERS };
  /** 0..1 speed multiplier for the hand (lower confidence = slower). */
  speedScale = 1;

  private candidate: GestureId | null = null;
  private candidateSince = 0;

  ingest(t: Telemetry, nowMs: number): void {
    this.confidence = t.confidence;

    // Gesture label state machine (debounced).
    if (t.confidence >= MIN_ACCEPT_CONFIDENCE) {
      if (this.phase === 'safe') {
        this.current = t.gesture;
        this.phase = 'transitioning';
        this.candidate = null;
      } else if (t.gesture !== this.current) {
        if (this.candidate !== t.gesture) {
          this.candidate = t.gesture;
          this.candidateSince = nowMs;
        } else if (nowMs - this.candidateSince >= DEBOUNCE_MS) {
          this.current = t.gesture;
          this.phase = 'transitioning';
          this.candidate = null;
        }
      } else {
        this.candidate = null;
      }
    }

    // Finger targets, softened by confidence.
    const w = t.confidence < 0.2 ? 0 : smoothstep(0.3, 0.85, t.confidence);
    for (const f of FINGER_IDS) {
      this.targets[f] += (clamp(t.fingers[f], 0, 1) - this.targets[f]) * w;
    }
    this.speedScale = 0.35 + 0.65 * w;
  }

  /** Manual gesture selection from the UI. */
  forceGesture(g: GestureId): void {
    this.current = g;
    this.candidate = null;
    this.phase = 'transitioning';
    this.confidence = 1;
    this.speedScale = 1;
    Object.assign(this.targets, GESTURE_PROFILES[g].pose);
  }

  /** Go to Rest and stay there until valid data arrives. */
  enterSafe(reason: string): void {
    this.current = 'rest';
    this.candidate = null;
    this.phase = 'safe';
    this.confidence = 0;
    this.safeReason = reason;
    this.speedScale = 0.6;
    Object.assign(this.targets, GESTURE_PROFILES.rest.pose);
  }

  update(fingersSettled: boolean): void {
    if (this.phase === 'transitioning' && fingersSettled) this.phase = 'holding';
  }

  static isGestureId(v: string): v is GestureId {
    return (GESTURE_IDS as readonly string[]).includes(v);
  }
}

