import {
  AxesHelper,
  BufferGeometry,
  CircleGeometry,
  Color,
  CylinderGeometry,
  DoubleSide,
  Euler,
  Group,
  Matrix4,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  Object3D,
  Quaternion,
  SphereGeometry,
  Vector3,
} from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { FINGER_IDS, type EmgFrame, type FingerId, type FingerValues, type ImuAngles } from '../types/telemetry';
import { FINGER_SPECS, clamp, type FingerSpec } from './JointLimits';
import { FingerController } from './FingerController';

const DEG2RAD = Math.PI / 180;
const ARC_SEGMENTS = 24;
const SKIN_COLOR = 0xd9a184;

interface JointVisual {
  arcGeo: BufferGeometry;
  arcMesh: Mesh;
  arcMat: MeshBasicMaterial;
}

interface FingerVisual {
  mat: MeshStandardMaterial;
  joints: JointVisual[];
}

export interface ModelLoadResult {
  ok: boolean;
  message: string;
}

/** Sphere pushed towards a rounded box (exponent < 1 squares the silhouette in X/Y). */
function superEllipsoid(exponent: number): SphereGeometry {
  const g = new SphereGeometry(1, 64, 48);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i);
    const y = p.getY(i);
    p.setXYZ(i, Math.sign(x) * Math.abs(x) ** exponent, Math.sign(y) * Math.abs(y) ** exponent, p.getZ(i));
  }
  g.computeVertexNormals();
  return g;
}

/**
 * Hierarchical, fully virtual three-finger right hand with an organic (skin-like) look.
 *
 * VirtualHand (root)
 * ├── VirtualForearm (static)
 * └── WristPivot (rotated by IMU about the wrist)
 *     ├── Palm (rounded palm, thenar and hypothenar pads)
 *     ├── Thumb → ThumbBase → ThumbJoint → ThumbTip
 *     ├── IndexFinger → IndexMCP → IndexPIP → IndexDIP → IndexTip
 *     └── MiddleFinger → MiddleMCP → MiddlePIP → MiddleDIP → MiddleTip
 *
 * Seen from the palm side (+Z) the thumb is on the +X side (right hand). Finger roots
 * start inside the palm so each finger grows out of the palm surface without a seam.
 */
export class VirtualHand {
  readonly root = new Group();
  /** Rotated by the virtual IMU about the wrist; holds palm and fingers. */
  readonly pivot = new Group();
  readonly fingers: Record<FingerId, FingerController>;

  private readonly skinMat = new MeshStandardMaterial({ color: SKIN_COLOR, roughness: 0.62, metalness: 0, emissive: 0x000000 });
  private readonly visuals = {} as Record<FingerId, FingerVisual>;
  private readonly proceduralParts: Object3D[] = [];
  private readonly proceduralJoints = {} as Record<FingerId, Object3D[]>;
  private readonly accent = new Color(0x7aa2c9);
  private readonly accentTarget = new Color(0x7aa2c9);
  private emgMean = 0;
  private glbRoot: Object3D | null = null;

  private readonly qPitch = new Quaternion();
  private readonly qRoll = new Quaternion();
  private readonly qYaw = new Quaternion();
  private readonly qTarget = new Quaternion();
  private static readonly X = new Vector3(1, 0, 0);
  private static readonly Y = new Vector3(0, 1, 0);
  private static readonly Z = new Vector3(0, 0, 1);

  constructor() {
    this.root.name = 'VirtualHand';
    this.pivot.name = 'WristPivot';
    this.root.add(this.pivot);
    this.buildArm();
    this.buildPalm();

    const thumb = this.buildFinger(FINGER_SPECS.thumb, new Vector3(0.44, 0.38, 0.08), new Euler(0.35, 0.55, -0.82));
    const index = this.buildFinger(FINGER_SPECS.index, new Vector3(0.25, 1.45, 0), new Euler());
    const middle = this.buildFinger(FINGER_SPECS.middle, new Vector3(-0.24, 1.47, 0), new Euler());
    this.pivot.add(thumb.group, index.group, middle.group);

    this.proceduralJoints.thumb = thumb.joints;
    this.proceduralJoints.index = index.joints;
    this.proceduralJoints.middle = middle.joints;
    this.fingers = {
      thumb: new FingerController(FINGER_SPECS.thumb, thumb.joints),
      index: new FingerController(FINGER_SPECS.index, index.joints),
      middle: new FingerController(FINGER_SPECS.middle, middle.joints),
    };
    for (const f of FINGER_IDS) this.fingers[f].snapTo(0.2);

    const axes = new AxesHelper(0.9);
    axes.name = 'WristAxes';
    this.pivot.add(axes);
  }

  // ───────────────────────── construction ─────────────────────────

  private blob(
    parent: Object3D,
    name: string,
    scale: [number, number, number],
    pos: [number, number, number],
    rotZ = 0,
    geo?: BufferGeometry,
    mat: MeshStandardMaterial = this.skinMat,
  ): Mesh {
    const m = new Mesh(geo ?? new SphereGeometry(1, 48, 32), mat);
    m.name = name;
    m.scale.set(...scale);
    m.position.set(...pos);
    m.rotation.z = rotZ;
    parent.add(m);
    return m;
  }

  private buildPalm(): void {
    const palm = new Group();
    palm.name = 'Palm';
    this.blob(palm, 'PalmBody', [0.6, 0.78, 0.24], [0.02, 0.86, 0], 0, superEllipsoid(0.62));
    this.blob(palm, 'PalmThenar', [0.33, 0.5, 0.24], [0.38, 0.48, 0.05], -0.35);
    this.blob(palm, 'PalmHypothenar', [0.26, 0.5, 0.2], [-0.36, 0.6, 0.03], 0.1);
    this.blob(palm, 'PalmHeel', [0.4, 0.3, 0.22], [0, 0.28, 0.01]);
    this.pivot.add(palm);
    this.proceduralParts.push(palm);
  }

  /** Virtual forearm and wrist (static, does not rotate with the wrist). */
  private buildArm(): void {
    const arm = new Group();
    arm.name = 'VirtualForearm';
    const forearm = new Mesh(new CylinderGeometry(0.43, 0.55, 2.2, 48, 1), this.skinMat);
    forearm.name = 'Forearm';
    forearm.scale.z = 0.72;
    forearm.position.y = -1.25;
    arm.add(forearm);
    const wrist = new Mesh(new CylinderGeometry(0.4, 0.44, 0.5, 48, 1, true), this.skinMat);
    wrist.name = 'Wrist';
    wrist.scale.z = 0.68;
    wrist.position.y = 0.05;
    arm.add(wrist);
    this.blob(arm, 'WristBlend', [0.43, 0.25, 0.3], [0, -0.18, 0]);
    this.root.add(arm);
    this.proceduralParts.push(arm);
  }

  private buildFinger(spec: FingerSpec, origin: Vector3, baseRot: Euler): { group: Group; joints: Object3D[] } {
    const group = new Group();
    group.name = spec.groupName;
    group.position.copy(origin);
    group.rotation.copy(baseRot);

    const mat = this.skinMat.clone();
    const jointVisuals: JointVisual[] = [];
    const joints: Object3D[] = [];
    const arcMatrix = new Matrix4().makeBasis(new Vector3(0, 1, 0), new Vector3(0, 0, 1), new Vector3(1, 0, 0));
    const arcOffsetX = spec.segmentRadius + 0.08;

    let parent: Object3D = group;
    let rad = spec.segmentRadius;
    spec.joints.forEach((limit, i) => {
      const joint = new Group();
      joint.name = limit.name;
      const prevLen = i > 0 ? spec.segmentLengths[i - 1] : 0;
      joint.position.y = prevLen;
      parent.add(joint);
      joints.push(joint);

      const segLen = spec.segmentLengths[i];
      const rTop = rad * 0.92;
      // Knuckle sphere matches the segment radius so joints stay flush (no bulge).
      this.blob(joint, `${limit.name}_Knuckle`, [rad, rad, rad * 0.9], [0, 0, 0], 0, undefined, mat);
      // The first segment widens slightly at its root, which sits inside the palm.
      const rBase = i === 0 ? rad * 1.12 : rad;
      const seg = new Mesh(new CylinderGeometry(rTop, rBase, segLen, 40, 1, true), mat);
      seg.name = `${limit.name}_Segment`;
      seg.scale.z = 0.9;
      seg.position.y = segLen / 2;
      joint.add(seg);
      if (i === spec.joints.length - 1) {
        this.blob(joint, `${limit.name}_Pad`, [rTop, rTop * 1.15, rTop * 0.9], [0, segLen, 0], 0, undefined, mat);
      }

      // Angle arc, drawn in the parent's frame so it spans parent-segment → current direction.
      const arcGeo = new CircleGeometry(0.3, ARC_SEGMENTS, 0, limit.maxDeg * DEG2RAD);
      arcGeo.applyMatrix4(arcMatrix);
      const arcMat = new MeshBasicMaterial({ color: 0x33ff99, transparent: true, opacity: 0.45, side: DoubleSide, depthWrite: false });
      const arcMesh = new Mesh(arcGeo, arcMat);
      arcMesh.name = `${limit.name}_AngleArc`;
      arcMesh.position.set(arcOffsetX, prevLen, 0);
      arcMesh.visible = false;
      parent.add(arcMesh);
      jointVisuals.push({ arcGeo, arcMesh, arcMat });

      parent = joint;
      rad = rTop;
    });

    if (spec.tipNodeName) {
      const tip = new Group();
      tip.name = spec.tipNodeName;
      tip.position.y = spec.segmentLengths[spec.segmentLengths.length - 1];
      parent.add(tip);
    }

    this.visuals[spec.id] = { mat, joints: jointVisuals };
    this.proceduralParts.push(group);
    return { group, joints };
  }

  // ───────────────────────── runtime API ─────────────────────────

  setFingerTargets(values: FingerValues, speedScale = 1): void {
    for (const f of FINGER_IDS) {
      this.fingers[f].setTarget(values[f]);
      this.fingers[f].speedScale = speedScale;
    }
  }

  get settled(): boolean {
    return FINGER_IDS.every((f) => this.fingers[f].settled);
  }

  /** Smoothly rotates the whole hand about the wrist using virtual IMU angles (slerp). */
  setOrientation(imu: ImuAngles, dt: number): void {
    this.qPitch.setFromAxisAngle(VirtualHand.X, imu.pitch * DEG2RAD);
    this.qRoll.setFromAxisAngle(VirtualHand.Y, imu.roll * DEG2RAD);
    this.qYaw.setFromAxisAngle(VirtualHand.Z, -imu.yaw * DEG2RAD);
    this.qTarget.copy(this.qYaw).multiply(this.qPitch).multiply(this.qRoll);
    this.pivot.quaternion.slerp(this.qTarget, 1 - Math.exp(-12 * dt));
  }

  setAccent(color: number): void {
    this.accentTarget.setHex(color);
  }

  setEmg(frame: EmgFrame): void {
    let sum = 0;
    for (let i = 0; i < 4; i++) sum += frame[i];
    this.emgMean = sum / 4;
  }

  update(dt: number): void {
    this.accent.lerp(this.accentTarget, 1 - Math.exp(-6 * dt));
    // Subtle activity tint on the skin; a strong glow would break the organic look.
    this.skinMat.emissive.copy(this.accent);
    this.skinMat.emissiveIntensity = this.emgMean * 0.08;

    for (const id of FINGER_IDS) {
      const fc = this.fingers[id];
      fc.update(dt, this.emgMean);
      const vis = this.visuals[id];
      vis.mat.emissive.copy(this.accent);
      vis.mat.emissiveIntensity = fc.glow * 0.12;
      fc.spec.joints.forEach((limit, i) => {
        const jv = vis.joints[i];
        const frac = clamp((fc.jointAngles[i] - limit.minDeg) / (limit.maxDeg - limit.minDeg), 0, 1);
        jv.arcMat.color.setHSL(0.38 * (1 - frac), 0.95, 0.55);
        const count = Math.ceil(frac * ARC_SEGMENTS) * 3;
        jv.arcMesh.visible = count > 0 && this.glbRoot === null;
        jv.arcGeo.setDrawRange(0, count);
      });
    }
  }

  /** Reset to a neutral relaxed hand without animation. */
  snapReset(rest: FingerValues): void {
    for (const f of FINGER_IDS) this.fingers[f].snapTo(rest[f]);
    this.pivot.quaternion.identity();
  }

  // ───────────────────────── GLB support ─────────────────────────

  /**
   * Loads a GLB/GLTF whose joint nodes use the same names as the procedural rig
   * (ThumbBase, ThumbJoint, ThumbTip, IndexMCP, IndexPIP, IndexDIP, IndexTip, Middle…).
   * If any joint is missing the procedural model is kept.
   */
  async loadModel(source: File | string): Promise<ModelLoadResult> {
    const loader = new GLTFLoader();
    try {
      const gltf =
        typeof source === 'string' ? await loader.loadAsync(source) : await loader.parseAsync(await source.arrayBuffer(), '');
      const scene = gltf.scene;
      const bound: Record<FingerId, Object3D[]> = { thumb: [], index: [], middle: [] };
      const missing: string[] = [];
      for (const id of FINGER_IDS) {
        for (const j of FINGER_SPECS[id].joints) {
          const node = scene.getObjectByName(j.name);
          if (node) bound[id].push(node);
          else missing.push(j.name);
        }
      }
      if (missing.length > 0) return { ok: false, message: `Model ignored. Missing nodes: ${missing.join(', ')}` };

      this.resetModel();
      for (const p of this.proceduralParts) p.visible = false;
      this.pivot.add(scene);
      this.glbRoot = scene;
      for (const id of FINGER_IDS) this.fingers[id].bindJoints(bound[id]);
      return { ok: true, message: 'GLB rig bound to the virtual hand.' };
    } catch {
      return { ok: false, message: 'Could not read the model file.' };
    }
  }

  /** Go back to the built-in procedural model. */
  resetModel(): void {
    if (this.glbRoot) {
      this.pivot.remove(this.glbRoot);
      this.glbRoot = null;
    }
    for (const p of this.proceduralParts) p.visible = true;
    for (const id of FINGER_IDS) {
      for (const j of this.proceduralJoints[id]) j.quaternion.identity(); // rest pose = identity
      this.fingers[id].bindJoints(this.proceduralJoints[id]);
    }
  }
}
