import { DirectionalLight, HemisphereLight, PointLight, type Scene } from 'three';

export class Lighting {
  constructor(scene: Scene) {
    scene.add(new HemisphereLight(0xbcd7ff, 0x0b1220, 0.9));

    const key = new DirectionalLight(0xffffff, 2.2);
    key.position.set(4, 7, 6);
    scene.add(key);

    const rim = new PointLight(0x38bdf8, 18, 14, 1.6);
    rim.position.set(-4, 3, -3);
    scene.add(rim);

    const fill = new PointLight(0xa78bfa, 10, 12, 1.6);
    fill.position.set(4, 0.5, 3);
    scene.add(fill);
  }
}

