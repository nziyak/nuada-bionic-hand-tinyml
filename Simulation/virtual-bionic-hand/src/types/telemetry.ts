/**
 * Shared type definitions for the fully virtual bionic hand simulation.
 * Nothing here maps to real hardware: all values only drive the 3D model and the UI.
 */

export const GESTURE_IDS = [
  'rest',
  'open_hand',
  'power_grasp',
  'fist',
  'pinch_grasp',
  'pointing',
  'partial_grasp',
  'thumb_index_contact',
  'thumb_middle_contact',
] as const;
export type GestureId = (typeof GESTURE_IDS)[number];

export const FINGER_IDS = ['thumb', 'index', 'middle'] as const;
export type FingerId = (typeof FINGER_IDS)[number];

/** Normalised flexion per finger: 0 = fully extended, 1 = fully flexed. */
export type FingerValues = Record<FingerId, number>;

/** Virtual MPU-6050 style orientation, in degrees. */
export interface ImuAngles {
  pitch: number;
  roll: number;
  yaw: number;
}
export type ImuAxis = keyof ImuAngles;

/** Four virtual sEMG channels (normalised envelope 0..1). */
export type EmgFrame = [number, number, number, number];

export interface Telemetry {
  /** Source timestamp (passed through, only used for display). */
  timestamp: number;
  gesture: GestureId;
  /** 0..1 */
  confidence: number;
  fingers: FingerValues;
  /** True when the packet carried explicit finger values (otherwise derived from gesture). */
  hasExplicitFingers: boolean;
  imu: ImuAngles;
  emg: EmgFrame;
  inferenceLatencyMs: number;
}

export type TelemetryListener = (telemetry: Telemetry) => void;
export type InvalidListener = (reason: string) => void;

export type DataMode = 'simulation' | 'live';

export type ConnectionStatus = 'idle' | 'connecting' | 'open' | 'closed' | 'error';

export type StatusLevel = 'ok' | 'warn' | 'error';

export interface GestureProfile {
  id: GestureId;
  label: string;
  description: string;
  /** Accent colour as hex number. */
  color: number;
  pose: FingerValues;
}

