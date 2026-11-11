// Dev check: fingertip distances per gesture (headless, no rendering).
import { Vector3 } from 'three';
import { VirtualHand } from '../src/hand/VirtualHand';
import { GESTURE_PROFILES } from '../src/hand/GestureController';
import { FINGER_IDS, GESTURE_IDS } from '../src/types/telemetry';

const hand = new VirtualHand();
const tipOf = (name: string, extra: number): Vector3 => {
  const n = hand.root.getObjectByName(name);
  if (!n) throw new Error(name);
  return new Vector3(0, extra, 0).applyMatrix4(n.matrixWorld);
};
for (const g of GESTURE_IDS) {
  const p = GESTURE_PROFILES[g].pose;
  for (const f of FINGER_IDS) hand.fingers[f].snapTo(p[f]);
  hand.root.updateMatrixWorld(true);
  const t = tipOf('ThumbTip', 0.38 + 0.1);
  const i = tipOf('IndexTip', 0.1);
  const m = tipOf('MiddleTip', 0.1);
  console.log(g.padEnd(22), 'thumb-index', t.distanceTo(i).toFixed(2), 'thumb-middle', t.distanceTo(m).toFixed(2),
    'idx z', i.z.toFixed(2), 'idx y', i.y.toFixed(2));
}

