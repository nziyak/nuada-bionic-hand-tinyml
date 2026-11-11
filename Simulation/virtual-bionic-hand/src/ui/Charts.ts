import type { EmgFrame } from '../types/telemetry';
import { EMG_CHANNEL_NAMES } from '../sensors/VirtualEMG';

const CHANNEL_COLORS = ['#4dd0ff', '#3ddc97', '#ffd23f', '#ff6b9a'];
const HISTORY = 240;

/** Scrolling 4-channel virtual sEMG plot on a 2D canvas. */
export class EmgChart {
  private readonly ctx: CanvasRenderingContext2D;
  private readonly history: Float32Array[] = [];
  private head = 0;
  private count = 0;
  private width = 300;
  private height = 150;
  private lastDraw = 0;
  private readonly legendValues: HTMLElement[] = [];

  constructor(
    private readonly canvas: HTMLCanvasElement,
    legend: HTMLElement,
  ) {
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('2D canvas not supported');
    this.ctx = ctx;
    for (let i = 0; i < 4; i++) this.history.push(new Float32Array(HISTORY));

    EMG_CHANNEL_NAMES.forEach((name, i) => {
      const cell = document.createElement('div');
      cell.style.borderBottomColor = CHANNEL_COLORS[i];
      const label = document.createElement('span');
      label.textContent = `CH${i + 1} ${name}`;
      const value = document.createElement('b');
      value.textContent = '0.00';
      cell.append(label, value);
      legend.appendChild(cell);
      this.legendValues.push(value);
    });

    new ResizeObserver(() => this.resize()).observe(canvas);
    this.resize();
  }

  private resize(): void {
    const dpr = Math.min(window.devicePixelRatio, 2);
    this.width = Math.max(10, this.canvas.clientWidth);
    this.height = Math.max(10, this.canvas.clientHeight);
    this.canvas.width = Math.round(this.width * dpr);
    this.canvas.height = Math.round(this.height * dpr);
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  push(frame: EmgFrame): void {
    for (let i = 0; i < 4; i++) this.history[i][this.head] = frame[i];
    this.head = (this.head + 1) % HISTORY;
    this.count = Math.min(this.count + 1, HISTORY);
  }

  /** Draws at most ~30 times per second. */
  draw(nowMs: number): void {
    if (nowMs - this.lastDraw < 33) return;
    this.lastDraw = nowMs;
    const { ctx, width: w, height: h } = this;
    ctx.clearRect(0, 0, w, h);

    ctx.strokeStyle = 'rgba(120,150,190,0.14)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 1; i < 4; i++) {
      const y = (h / 4) * i;
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
    }
    ctx.stroke();

    const laneH = h / 4;
    for (let c = 0; c < 4; c++) {
      const buf = this.history[c];
      ctx.strokeStyle = CHANNEL_COLORS[c];
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      const base = laneH * (c + 1) - 3;
      for (let i = 0; i < this.count; i++) {
        const idx = (this.head - this.count + i + HISTORY * 2) % HISTORY;
        const x = w - ((this.count - 1 - i) / (HISTORY - 1)) * w;
        const y = base - buf[idx] * (laneH - 8);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      const last = this.count > 0 ? buf[(this.head - 1 + HISTORY) % HISTORY] : 0;
      this.legendValues[c].textContent = last.toFixed(2);
    }
  }
}

