// Dev check: find flexion pairs where thumb tip meets index / middle tip (headless).
import { Vector3 } from 'three';
import { VirtualHand } from '../src/hand/VirtualHand';

const hand = new VirtualHand();
const tipOf = (name: string, extra: number): Vector3 => {
  const n = hand.root.getObjectByName(name);
  if (!n) throw new Error(name);
  return new Vector3(0, extra, 0).applyMatrix4(n.matrixWorld);
};
for (const [fid, tip] of [['index', 'IndexTip'], ['middle', 'MiddleTip']] as const) {
  let best = { d: 99, t: 0, f: 0 };
  for (let t = 0; t <= 1.001; t += 0.05) {
    for (let f = 0; f <= 1.001; f += 0.05) {
      hand.fingers.thumb.snapTo(t);
      hand.fingers[fid].snapTo(f);
      hand.root.updateMatrixWorld(true);
      const d = tipOf('ThumbTip', 0.48).distanceTo(tipOf(tip, 0.1));
      if (d < best.d) best = { d, t, f };
    }
  }
  console.log(fid, 'best distance', best.d.toFixed(2), 'thumb', best.t.toFixed(2), 'finger', best.f.toFixed(2));
}

