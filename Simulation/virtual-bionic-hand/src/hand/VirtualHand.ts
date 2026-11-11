import {
  AxesHelper,
  BufferGeometry,
  CircleGeometry,
  Color,
  CylinderGeometry,
  DoubleSide,
  EdgesGeometry,
  ExtrudeGeometry,
  Shape,
  TorusGeometry,
  Group,
  LineBasicMaterial,
  LineSegments,
  Matrix4,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  Object3D,
  PlaneGeometry,
  Quaternion,
  SphereGeometry,
  Vector3,
} from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { FINGER_IDS, type EmgFrame, type FingerId, type FingerValues, type ImuAngles } from '../types/telemetry';
import { FINGER_SPECS, clamp, type FingerSpec } from './JointLimits';
import { FingerController } from './FingerController';
import { emgHue } from '../sensors/VirtualEMG';

const DEG2RAD = Math.PI / 180;
const ARC_SEGMENTS = 24;

interface JointVisual {
  indicatorMat: MeshStandardMaterial;
  arcGeo: BufferGeometry;
  arcMesh: Mesh;
  arcMat: MeshBasicMaterial;
}

interface FingerVisual {
  segMats: MeshStandardMaterial[];
  joints: JointVisual[];
  tipMat: MeshStandardMaterial | null;
}

export interface ModelLoadResult {
  ok: boolean;
  message: string;
}

/**
 * Hierarchical, fully virtual three-finger hand.
 *
 * VirtualHand (root, rotated by IMU about the wrist)
 * ├── Palm
 * ├── Thumb → ThumbBase → ThumbJoint → ThumbTip
 * ├── IndexFinger → IndexMCP → IndexPIP → IndexDIP → IndexTip
 * └── MiddleFinger → MiddleMCP → MiddlePIP → MiddleDIP → MiddleTip
 *
 * Joints are nested so that each one inherits its parent's rotation, while every
 * joint can still be rotated independently.
 */
export class VirtualHand {
  readonly root = new Group();
  /** Rotated by the virtual IMU about the wrist; holds palm and fingers. */
  readonly pivot = new Group();
  readonly fingers: Record<FingerId, FingerController>;

  private readonly accentMat = new MeshBasicMaterial({ color: 0x7aa2c9 });
  private readonly cuffMat = new MeshStandardMaterial({ color: 0x1a2533, metalness: 0.8, roughness: 0.3 });

  private readonly palmMat = new MeshStandardMaterial({ color: 0x2b3a4d, metalness: 0.6, roughness: 0.4, emissive: 0x7aa2c9, emissiveIntensity: 0.15 });
  private readonly palmEdgeMat = new LineBasicMaterial({ color: 0x7aa2c9, transparent: true, opacity: 0.8 });
  private readonly emgPadMats: MeshBasicMaterial[] = [];
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

    const thumb = this.buildFinger(FINGER_SPECS.thumb, new Vector3(-0.55, 0.45, 0.12), 0.6);
    const index = this.buildFinger(FINGER_SPECS.index, new Vector3(-0.28, 1.6, 0), 0);
    const middle = this.buildFinger(FINGER_SPECS.middle, new Vector3(0.28, 1.6, 0), 0);
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

  private buildPalm(): void {
    // Anatomical-style outline: narrow wrist widening to the knuckle line, softly rounded.
    const s = new Shape();
    s.moveTo(-0.36, 0);
    s.lineTo(0.36, 0);
    s.bezierCurveTo(0.5, 0.3, 0.68, 0.8, 0.62, 1.3);
    s.bezierCurveTo(0.6, 1.58, 0.36, 1.74, 0, 1.74);
    s.bezierCurveTo(-0.36, 1.74, -0.6, 1.58, -0.62, 1.3);
    s.bezierCurveTo(-0.68, 0.8, -0.5, 0.3, -0.36, 0);
    const geo = new ExtrudeGeometry(s, {
      depth: 0.22,
      bevelEnabled: true,
      bevelThickness: 0.1,
      bevelSize: 0.1,
      bevelSegments: 6,
      curveSegments: 24,
    });
    geo.translate(0, 0, -0.11);
    const palm = new Mesh(geo, this.palmMat);
    palm.name = 'Palm';
    const edges = new LineSegments(new EdgesGeometry(geo, 60), this.palmEdgeMat);
    palm.add(edges);

    // Soft thumb-base (thenar) swelling so the thumb flows out of the palm.
    const thenar = new Mesh(new SphereGeometry(0.4, 28, 20), this.palmMat);
    thenar.name = 'PalmThenar';
    thenar.scale.set(0.85, 1.25, 0.6);
    thenar.position.set(-0.42, 0.5, 0.04);
    palm.add(thenar);

    // Digital sEMG heat indicators (flat screens on the virtual palm).
    const padGeo = new PlaneGeometry(0.15, 0.4);
    for (let i = 0; i < 4; i++) {
      const mat = new MeshBasicMaterial({ color: 0x1e5aa8 });
      const pad = new Mesh(padGeo, mat);
      pad.position.set(-0.33 + i * 0.22, 0.55, 0.222);
      pad.name = `EmgIndicator${i + 1}`;
      palm.add(pad);
      this.emgPadMats.push(mat);
    }

    this.pivot.add(palm);
    this.proceduralParts.push(palm);
  }

  /** Stylised virtual forearm (static, does not rotate with the wrist). */
  private buildArm(): void {
    const arm = new Group();
    arm.name = 'VirtualForearm';
    const body = new Mesh(new CylinderGeometry(0.46, 0.62, 3.2, 40, 1), this.palmMat);
    body.position.y = -0.1 - 1.6;
    arm.add(body);
    // Accent rings (digital display bands).
    for (const [y, r] of [[-0.35, 0.49], [-1.2, 0.54], [-2.1, 0.59]] as const) {
      const ring = new Mesh(new TorusGeometry(r, 0.025, 10, 48), this.accentMat);
      ring.rotation.x = Math.PI / 2;
      ring.position.y = y;
      arm.add(ring);
    }
    // Wrist joint cuff.
    const cuff = new Mesh(new CylinderGeometry(0.5, 0.5, 0.16, 40), this.cuffMat);
    cuff.position.y = -0.04;
    arm.add(cuff);
    this.root.add(arm);
    this.proceduralParts.push(arm);
  }

  private buildFinger(
    spec: FingerSpec,
    origin: Vector3,
    baseRotZ: number,
  ): { group: Group; joints: Object3D[] } {
    const group = new Group();
    group.name = spec.groupName;
    group.position.copy(origin);
    group.rotation.z = baseRotZ;

    // Smooth flared sleeve blending the finger root into the palm (no stick-on look).
    const rb = spec.segmentRadius;
    const blend = new Mesh(new CylinderGeometry(rb * 1.02, rb * 1.5, 0.55, 28, 1), this.palmMat);
    blend.name = `${spec.groupName}_Blend`;
    blend.scale.z = 0.85;
    blend.position.y = -0.22;
    group.add(blend);

    const segMats: MeshStandardMaterial[] = [];
    const jointVisuals: JointVisual[] = [];
    const joints: Object3D[] = [];
    const arcMatrix = new Matrix4().makeBasis(new Vector3(0, 1, 0), new Vector3(0, 0, 1), new Vector3(1, 0, 0));
    const tones = [0.34, 0.42, 0.52];
    const jointGeo = new SphereGeometry(spec.segmentRadius * 0.72, 20, 14);
    const arcOffsetX = spec.segmentRadius + 0.06;

    let parent: Object3D = group;
    spec.joints.forEach((limit, i) => {
      const joint = new Group();
      joint.name = limit.name;
      const prevLen = i > 0 ? spec.segmentLengths[i - 1] : 0;
      joint.position.y = prevLen;
      parent.add(joint);
      joints.push(joint);

      const segLen = spec.segmentLengths[i];
      const color = new Color().setHSL(spec.hue, 0.55, tones[i % tones.length]);
      const segMat = new MeshStandardMaterial({ color, metalness: 0.55, roughness: 0.38, emissive: color, emissiveIntensity: 0.08 });
      segMats.push(segMat);
      // Tapered, slightly flattened segment with a visible gap at the joint (technical, not sausage-like).
      const rBase = spec.segmentRadius * (1 - 0.1 * i);
      const rTop = rBase * 0.82;
      const bodyLen = segLen * 0.88;
      const seg = new Mesh(new CylinderGeometry(rTop, rBase, bodyLen, 20, 1), segMat);
      seg.name = `${limit.name}_Segment`;
      seg.scale.z = 0.85;
      seg.position.y = segLen * 0.06 + bodyLen / 2;
      joint.add(seg);
      if (i === spec.joints.length - 1) {
        const cap = new Mesh(new SphereGeometry(rTop, 20, 14), segMat);
        cap.name = `${limit.name}_Pad`;
        cap.scale.z = 0.85;
        cap.position.y = segLen * 0.06 + bodyLen;
        joint.add(cap);
      }

      const indicatorMat = new MeshStandardMaterial({ color: 0x10202e, metalness: 0.2, roughness: 0.3, emissive: 0x33ff99, emissiveIntensity: 0.5 });
      const indicator = new Mesh(jointGeo, indicatorMat);
      indicator.name = `${limit.name}_Indicator`;
      joint.add(indicator);

      // Angle arc, drawn in the parent's frame so it spans parent-segment → current direction.
      const arcGeo = new CircleGeometry(0.3, ARC_SEGMENTS, 0, limit.maxDeg * DEG2RAD);
      arcGeo.applyMatrix4(arcMatrix);
      const arcMat = new MeshBasicMaterial({ color: 0x33ff99, transparent: true, opacity: 0.55, side: DoubleSide, depthWrite: false });
      const arcMesh = new Mesh(arcGeo, arcMat);
      arcMesh.name = `${limit.name}_AngleArc`;
      arcMesh.position.set(arcOffsetX, prevLen, 0);
      arcMesh.visible = false;
      parent.add(arcMesh);
      jointVisuals.push({ indicatorMat, arcGeo, arcMesh, arcMat });

      parent = joint;
    });

    let tipMat: MeshStandardMaterial | null = null;
    if (spec.tipNodeName) {
      const tip = new Group();
      tip.name = spec.tipNodeName;
      tip.position.y = spec.segmentLengths[spec.segmentLengths.length - 1];
      parent.add(tip);
      tipMat = new MeshStandardMaterial({ color: 0x10202e, emissive: new Color().setHSL(spec.hue, 0.9, 0.6), emissiveIntensity: 0.4 });
      const tipMesh = new Mesh(new SphereGeometry(spec.segmentRadius * 0.75, 16, 12), tipMat);
      tipMesh.name = `${spec.tipNodeName}_Marker`;
      tipMesh.position.y = spec.segmentRadius * 0.6;
      tip.add(tipMesh);
    }

    this.visuals[spec.id] = { segMats, joints: jointVisuals, tipMat };
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
    for (let i = 0; i < 4; i++) {
      this.emgPadMats[i].color.setHSL(emgHue(frame[i]), 0.85, 0.28 + frame[i] * 0.3);
      sum += frame[i];
    }
    this.emgMean = sum / 4;
  }

  update(dt: number): void {
    this.accent.lerp(this.accentTarget, 1 - Math.exp(-6 * dt));
    this.palmMat.emissive.copy(this.accent);
    this.palmMat.emissiveIntensity = 0.12 + this.emgMean * 0.5;
    this.palmEdgeMat.color.copy(this.accent);
    this.accentMat.color.copy(this.accent);

    for (const id of FINGER_IDS) {
      const fc = this.fingers[id];
      fc.update(dt, this.emgMean);
      const vis = this.visuals[id];
      for (const m of vis.segMats) m.emissiveIntensity = 0.06 + fc.glow * 1.0;
      if (vis.tipMat) vis.tipMat.emissiveIntensity = 0.3 + fc.glow * 1.5;
      fc.spec.joints.forEach((limit, i) => {
        const jv = vis.joints[i];
        const frac = clamp((fc.jointAngles[i] - limit.minDeg) / (limit.maxDeg - limit.minDeg), 0, 1);
        jv.indicatorMat.emissive.setHSL(0.38 * (1 - frac), 0.95, 0.5);
        jv.indicatorMat.emissiveIntensity = 0.45 + frac * 0.9;
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
