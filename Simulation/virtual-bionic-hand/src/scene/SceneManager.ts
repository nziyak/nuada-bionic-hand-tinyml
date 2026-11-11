import {
  ACESFilmicToneMapping,
  Color,
  Fog,
  GridHelper,
  Scene,
  WebGLRenderer,
  type Material,
  type Object3D,
} from 'three';
import { CameraManager } from './CameraManager';
import { Lighting } from './Lighting';

/** Owns renderer, scene, camera and the laboratory-style backdrop. */
export class SceneManager {
  readonly scene = new Scene();
  readonly renderer: WebGLRenderer;
  readonly cameraManager: CameraManager;
  private readonly resizeObserver: ResizeObserver;

  constructor(private readonly container: HTMLElement) {
    this.renderer = new WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    container.appendChild(this.renderer.domElement);

    this.scene.background = new Color(0x0a111c);
    this.scene.fog = new Fog(0x0a111c, 12, 30);

    this.cameraManager = new CameraManager(this.renderer.domElement);
    new Lighting(this.scene);
    this.buildBackdrop();

    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(container);
    this.resize();
  }

  private buildBackdrop(): void {
    const floor = new GridHelper(24, 48, 0x2f6f9f, 0x16283a);
    floor.position.y = -3.5;
    this.scene.add(floor);

    const wall = new GridHelper(24, 48, 0x2a4a6b, 0x122234);
    wall.rotation.x = Math.PI / 2;
    wall.position.set(0, 10.7, -6);
    this.scene.add(wall);
    for (const g of [floor, wall]) {
      const mats = Array.isArray(g.material) ? g.material : [g.material];
      for (const m of mats as Material[]) {
        m.transparent = true;
        m.opacity = 0.6;
      }
    }
  }

  add(obj: Object3D): void {
    this.scene.add(obj);
  }

  private resize(): void {
    const w = Math.max(1, this.container.clientWidth);
    const h = Math.max(1, this.container.clientHeight);
    this.renderer.setSize(w, h, false);
    this.renderer.domElement.style.width = '100%';
    this.renderer.domElement.style.height = '100%';
    this.cameraManager.setAspect(w / h);
  }

  update(dt: number): void {
    this.cameraManager.update(dt);
  }

  render(): void {
    this.renderer.render(this.scene, this.cameraManager.camera);
  }

  dispose(): void {
    this.resizeObserver.disconnect();
    this.cameraManager.dispose();
    this.renderer.dispose();
  }
}

