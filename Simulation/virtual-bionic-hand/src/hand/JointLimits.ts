import type { FingerId, FingerValues, ImuAngles } from '../types/telemetry';

/** Virtual limit of one joint, in degrees. */
export interface JointLimit {
  name: string;
  minDeg: number;
  maxDeg: number;
  /** Local rotation axis (flexion). Normalised on use. */
  axis: readonly [number, number, number];
}

export interface FingerSpec {
  id: FingerId;
  label: string;
  /** Name of the Object3D group that holds the finger. */
  groupName: string;
  joints: JointLimit[];
  /** Length of the segment that follows each joint. */
  segmentLengths: number[];
  segmentRadius: number;
  /** Static tip marker node, for fingers whose last joint is not named "Tip". */
  tipNodeName?: string;
  /** Maximum flexion change per second (normalised units/s). */
  maxSpeed: number;
  /** Exponential smoothing coefficient (1/s). Higher = snappier. */
  smoothing: number;
  /** Allowed virtual flexion window (normalised). */
  minFlex: number;
  maxFlex: number;
  hue: number;
}

export const FINGER_SPECS: Record<FingerId, FingerSpec> = {
  thumb: {
    id: 'thumb',
    label: 'Thumb',
    groupName: 'Thumb',
    joints: [
      { name: 'ThumbBase', minDeg: 0, maxDeg: 75, axis: [1, 0, -1.1] },
      { name: 'ThumbJoint', minDeg: 0, maxDeg: 70, axis: [1, 0, -1.0] },
      { name: 'ThumbTip', minDeg: 0, maxDeg: 50, axis: [1, 0, -0.8] },
    ],
    segmentLengths: [0.55, 0.45, 0.38],
    segmentRadius: 0.19,
    maxSpeed: 2.4,
    smoothing: 9,
    minFlex: 0,
    maxFlex: 1,
    hue: 0.5,
  },
  index: {
    id: 'index',
    label: 'Index',
    groupName: 'IndexFinger',
    joints: [
      { name: 'IndexMCP', minDeg: 0, maxDeg: 90, axis: [1, 0, 0] },
      { name: 'IndexPIP', minDeg: 0, maxDeg: 105, axis: [1, 0, 0] },
      { name: 'IndexDIP', minDeg: 0, maxDeg: 75, axis: [1, 0, 0] },
    ],
    segmentLengths: [0.65, 0.45, 0.35],
    segmentRadius: 0.165,
    tipNodeName: 'IndexTip',
    maxSpeed: 3.0,
    smoothing: 11,
    minFlex: 0,
    maxFlex: 1,
    hue: 0.6,
  },
  middle: {
    id: 'middle',
    label: 'Middle',
    groupName: 'MiddleFinger',
    joints: [
      { name: 'MiddleMCP', minDeg: 0, maxDeg: 90, axis: [1, 0, 0] },
      { name: 'MiddlePIP', minDeg: 0, maxDeg: 105, axis: [1, 0, 0] },
      { name: 'MiddleDIP', minDeg: 0, maxDeg: 75, axis: [1, 0, 0] },
    ],
    segmentLengths: [0.72, 0.5, 0.38],
    segmentRadius: 0.17,
    tipNodeName: 'MiddleTip',
    maxSpeed: 3.0,
    smoothing: 11,
    minFlex: 0,
    maxFlex: 1,
    hue: 0.72,
  },
};

export const IMU_LIMITS: Record<keyof ImuAngles, { min: number; max: number }> = {
  pitch: { min: -80, max: 80 },
  roll: { min: -90, max: 90 },
  yaw: { min: -90, max: 90 },
};

export const REST_FINGERS: FingerValues = { thumb: 0.25, index: 0.2, middle: 0.2 };

export function clamp(v: number, lo: number, hi: number): number {
  return v < lo ? lo : v > hi ? hi : v;
}

export function clampImu(a: ImuAngles): ImuAngles {
  return {
    pitch: clamp(a.pitch, IMU_LIMITS.pitch.min, IMU_LIMITS.pitch.max),
    roll: clamp(a.roll, IMU_LIMITS.roll.min, IMU_LIMITS.roll.max),
    yaw: clamp(a.yaw, IMU_LIMITS.yaw.min, IMU_LIMITS.yaw.max),
  };
}

/** Joint angle (degrees) for a given flexion, always inside the virtual limits. */
export function jointAngleDeg(limit: JointLimit, flex: number): number {
  const f = clamp(flex, 0, 1);
  return limit.minDeg + (limit.maxDeg - limit.minDeg) * f;
}

