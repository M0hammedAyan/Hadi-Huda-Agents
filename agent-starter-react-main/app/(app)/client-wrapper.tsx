"use client";
import { ConnectivityPanel } from '@/components/app/connectivity-panel';
import { HadiHudaControls } from '@/components/app/hadi-huda-controls';

export default function ClientWrapper() {
  const handleConnect = (type: string, data: any) => {
    console.log(type, data);
    fetch('http://localhost:8003/api/status')
      .then(r => r.json())
      .then(d => console.log('Backend:', d))
      .catch(e => console.error('Backend error:', e));
  };

  return (
    <div className="space-y-4">
      <ConnectivityPanel onConnect={handleConnect} />
      <HadiHudaControls />
    </div>
  );
}