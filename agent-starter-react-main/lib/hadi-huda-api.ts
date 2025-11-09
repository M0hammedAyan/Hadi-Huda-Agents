// lib/hadi-huda-api.ts - API integration for Hadi-Huda backend
export interface HadiHudaAlert {
  type: 'hadi_alert' | 'huda_conversation' | 'agent_response';
  message: string;
  timestamp: number;
}

export class HadiHudaAPI {
  private ws: WebSocket | null = null;
  private listeners: ((alert: HadiHudaAlert) => void)[] = [];

  connect() {
    this.ws = new WebSocket('ws://localhost:8002/ws');
    
    this.ws.onmessage = (event) => {
      const alert: HadiHudaAlert = JSON.parse(event.data);
      this.listeners.forEach(listener => listener(alert));
    };
    
    return new Promise<void>((resolve, reject) => {
      if (!this.ws) return reject();
      this.ws.onopen = () => resolve();
      this.ws.onerror = reject;
    });
  }

  onAlert(callback: (alert: HadiHudaAlert) => void) {
    this.listeners.push(callback);
  }

  sendMessage(text: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'user_message',
        text: text
      }));
    }
  }

  async connectBluetooth() {
    const response = await fetch('http://localhost:8002/api/bluetooth/connect', {
      method: 'POST'
    });
    return response.json();
  }

  async playYoutube(videoId: string) {
    const response = await fetch('http://localhost:8003/api/youtube/play', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_id: videoId })
    });
    return response.json();
  }

  async getNearbyPlaces(type: string = 'gas_station') {
    const response = await fetch(`http://localhost:8003/api/maps/nearby?type=${type}`);
    return response.json();
  }
}