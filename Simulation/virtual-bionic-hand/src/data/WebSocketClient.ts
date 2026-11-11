import type { ConnectionStatus, InvalidListener, TelemetryListener } from '../types/telemetry';
import { parseTelemetry } from './DataParser';

export type StatusListener = (status: ConnectionStatus, detail: string) => void;

/**
 * Optional Live Data Mode source. Receives JSON text frames (e.g. from a
 * simulated ESP32-S3 telemetry server) and forwards validated telemetry.
 * It is receive-only: nothing is ever sent back and no hardware is controlled.
 */
export class WebSocketClient {
  private socket: WebSocket | null = null;
  private url = '';
  private wantConnected = false;
  private retryTimer: number | undefined;
  private retryMs = 1000;

  onTelemetry: TelemetryListener = () => undefined;
  onInvalid: InvalidListener = () => undefined;
  onStatus: StatusListener = () => undefined;

  connect(url: string): void {
    this.disconnect();
    this.url = url.trim();
    this.wantConnected = true;
    this.retryMs = 1000;
    this.open();
  }

  disconnect(): void {
    this.wantConnected = false;
    window.clearTimeout(this.retryTimer);
    if (this.socket) {
      this.socket.onopen = this.socket.onclose = this.socket.onerror = this.socket.onmessage = null;
      try {
        this.socket.close();
      } catch {
        /* ignore */
      }
      this.socket = null;
    }
    this.onStatus('idle', 'Disconnected');
  }

  private open(): void {
    if (!/^wss?:\/\//i.test(this.url)) {
      this.wantConnected = false;
      this.onStatus('error', 'URL must start with ws:// or wss://');
      return;
    }
    this.onStatus('connecting', `Connecting to ${this.url}…`);
    let socket: WebSocket;
    try {
      socket = new WebSocket(this.url);
    } catch {
      this.onStatus('error', 'Invalid WebSocket URL');
      this.scheduleRetry();
      return;
    }
    this.socket = socket;
    socket.onopen = () => {
      this.retryMs = 1000;
      this.onStatus('open', `Connected to ${this.url}`);
    };
    socket.onmessage = (ev: MessageEvent<unknown>) => {
      const result = parseTelemetry(ev.data);
      if (result.ok) this.onTelemetry(result.telemetry);
      else this.onInvalid(result.reason);
    };
    socket.onerror = () => this.onStatus('error', 'Connection error');
    socket.onclose = () => {
      this.socket = null;
      this.onStatus('closed', 'Connection closed');
      this.scheduleRetry();
    };
  }

  private scheduleRetry(): void {
    if (!this.wantConnected) return;
    window.clearTimeout(this.retryTimer);
    this.retryTimer = window.setTimeout(() => this.open(), this.retryMs);
    this.retryMs = Math.min(this.retryMs * 1.7, 6000);
  }
}

