import { PerspectiveCamera, Vector3 } from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

const HOME_POSITION = new Vector3(3.8, 2.4, 8.2);
const HOME_TARGET = new Vector3(0, 0.5, 0);

export class CameraManager {
  readonly camera: PerspectiveCamera;
  readonly controls: OrbitControls;
  private returning = false;

  constructor(dom: HTMLElement) {
    this.camera = new PerspectiveCamera(42, 1, 0.1, 100);
    this.camera.position.copy(HOME_POSITION);
    this.controls = new OrbitControls(this.camera, dom);
    this.controls.target.copy(HOME_TARGET);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.minDistance = 2.5;
    this.controls.maxDistance = 14;
    this.controls.maxPolarAngle = Math.PI * 0.95;
    this.controls.addEventListener('start', () => (this.returning = false));
    this.controls.update();
  }

  /** Smoothly animates back to the default view. */
  reset(): void {
    this.returning = true;
  }

  setAspect(aspect: number): void {
    this.camera.aspect = aspect;
    this.camera.updateProjectionMatrix();
  }

  update(dt: number): void {
    if (this.returning) {
      const k = 1 - Math.exp(-7 * dt);
      this.camera.position.lerp(HOME_POSITION, k);
      this.controls.target.lerp(HOME_TARGET, k);
      if (this.camera.position.distanceTo(HOME_POSITION) < 0.01 && this.controls.target.distanceTo(HOME_TARGET) < 0.01) {
        this.returning = false;
      }
    }
    this.controls.update();
  }

  dispose(): void {
    this.controls.dispose();
  }
}

