import {
  FINGER_IDS,
  type EmgFrame,
  type FingerValues,
  type GestureId,
  type ImuAngles,
  type Telemetry,
} from '../types/telemetry';
import { GESTURE_PROFILES } from '../hand/GestureController';
import { clamp, clampImu } from '../hand/JointLimits';

export type ParseResult = { ok: true; telemetry: Telemetry } | { ok: false; reason: string };

const MAX_MESSAGE_LENGTH = 8192;

const GESTURE_ALIASES: Record<string, GestureId> = {
  rest: 'rest',
  open: 'open_hand',
  open_hand: 'open_hand',
  power: 'power_grasp',
  power_grasp: 'power_grasp',
  fist: 'fist',
  pinch: 'pinch_grasp',
  pinch_grasp: 'pinch_grasp',
  point: 'pointing',
  pointing: 'pointing',
  partial: 'partial_grasp',
  partial_grasp: 'partial_grasp',
  thumb_index: 'thumb_index_contact',
  thumb_index_contact: 'thumb_index_contact',
  thumb_middle: 'thumb_middle_contact',
  thumb_middle_contact: 'thumb_middle_contact',
};

export function parseGestureId(value: unknown): GestureId | null {
  if (typeof value !== 'string') return null;
  const key = value.trim().toLowerCase().replace(/[\s-]+/g, '_');
  return GESTURE_ALIASES[key] ?? null;
}

class ParseError extends Error {}

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null && !Array.isArray(v);
}

/** Reads an optional finite number. Throws ParseError when present but invalid. */
function optionalNumber(obj: Record<string, unknown>, key: string): number | undefined {
  const v = obj[key];
  if (v === undefined || v === null) return undefined;
  if (typeof v !== 'number' || !Number.isFinite(v)) throw new ParseError(`"${key}" is not a finite number`);
  return v;
}

function normalizedFraction(obj: Record<string, unknown>, key: string): number | undefined {
  const v = optionalNumber(obj, key);
  if (v === undefined) return undefined;
  if (v < -0.05 || v > 1.05) throw new ParseError(`"${key}" out of range 0..1 (${v})`);
  return clamp(v, 0, 1);
}

/** Validates an already parsed JSON value and converts it to Telemetry. */
export function normalizeTelemetry(value: unknown): ParseResult {
  try {
    if (!isRecord(value)) throw new ParseError('payload is not a JSON object');

    const gesture = parseGestureId(value['gesture']);
    if (gesture === null) throw new ParseError(`unknown gesture "${String(value['gesture'])}"`);

    const confidence = normalizedFraction(value, 'confidence');
    if (confidence === undefined) throw new ParseError('"confidence" is missing');

    const pose = GESTURE_PROFILES[gesture].pose;
    const fingers: FingerValues = { ...pose };
    let hasExplicitFingers = false;
    for (const f of FINGER_IDS) {
      const v = normalizedFraction(value, f);
      if (v !== undefined) {
        fingers[f] = v;
        hasExplicitFingers = true;
      }
    }

    const imu: ImuAngles = clampImu({
      pitch: optionalNumber(value, 'pitch') ?? 0,
      roll: optionalNumber(value, 'roll') ?? 0,
      yaw: optionalNumber(value, 'yaw') ?? 0,
    });

    let emg: EmgFrame = [0, 0, 0, 0];
    const rawEmg = value['emg'];
    if (rawEmg !== undefined && rawEmg !== null) {
      if (!Array.isArray(rawEmg) || rawEmg.length !== 4) throw new ParseError('"emg" must be an array of 4 numbers');
      const out: number[] = [];
      for (const e of rawEmg as unknown[]) {
        if (typeof e !== 'number' || !Number.isFinite(e)) throw new ParseError('"emg" contains a non-numeric value');
        out.push(clamp(e, 0, 1));
      }
      emg = [out[0], out[1], out[2], out[3]];
    }

    const latency = optionalNumber(value, 'inference_latency_ms') ?? 0;

    return {
      ok: true,
      telemetry: {
        timestamp: optionalNumber(value, 'timestamp') ?? Date.now(),
        gesture,
        confidence,
        fingers,
        hasExplicitFingers,
        imu,
        emg,
        inferenceLatencyMs: clamp(latency, 0, 1000),
      },
    };
  } catch (err) {
    return { ok: false, reason: err instanceof ParseError ? err.message : 'unexpected payload error' };
  }
}

/** Parses a raw WebSocket message. Never throws. */
export function parseTelemetry(raw: unknown): ParseResult {
  if (typeof raw !== 'string') return { ok: false, reason: 'binary/non-text message' };
  if (raw.length > MAX_MESSAGE_LENGTH) return { ok: false, reason: 'message too large' };
  let json: unknown;
  try {
    json = JSON.parse(raw);
  } catch {
    return { ok: false, reason: 'malformed JSON' };
  }
  return normalizeTelemetry(json);
}

