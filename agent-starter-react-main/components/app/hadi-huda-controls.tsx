'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/livekit/button';
import { HadiHudaAPI, HadiHudaAlert } from '@/lib/hadi-huda-api';
import { Bluetooth, Youtube, MapPin, Music, Coffee } from 'lucide-react';

export function HadiHudaControls() {
  const [api] = useState(() => new HadiHudaAPI());
  const [alerts, setAlerts] = useState<HadiHudaAlert[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [bluetoothStatus, setBluetoothStatus] = useState('disconnected');
  const [message, setMessage] = useState('');

  useEffect(() => {
    api.connect().then(() => {
      setIsConnected(true);
      api.onAlert((alert) => {
        setAlerts(prev => [...prev.slice(-4), alert]);
      });
    });
  }, [api]);

  const handleBluetoothConnect = async () => {
    try {
      const result = await api.connectBluetooth();
      setBluetoothStatus(result.status);
    } catch (error) {
      console.error('Bluetooth connection failed:', error);
    }
  };

  const handleYouTubePlay = async () => {
    try {
      await api.playYoutube('relaxing-music-playlist');
    } catch (error) {
      console.error('YouTube play failed:', error);
    }
  };

  const handleFindNearby = async (type: string) => {
    try {
      const places = await api.getNearbyPlaces(type);
      console.log('Nearby places:', places);
    } catch (error) {
      console.error('Find nearby failed:', error);
    }
  };

  const sendMessage = () => {
    if (message.trim() && isConnected) {
      api.sendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="space-y-4 p-4 bg-gray-900 rounded-lg">
      <div className="flex items-center gap-2">
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-sm">Hadi-Huda {isConnected ? 'Connected' : 'Disconnected'}</span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <Button 
          onClick={handleBluetoothConnect}
          className="flex items-center gap-2"
          variant={bluetoothStatus === 'connected' ? 'default' : 'outline'}
        >
          <Bluetooth size={16} />
          Bluetooth
        </Button>

        <Button 
          onClick={handleYouTubePlay}
          className="flex items-center gap-2"
          variant="outline"
        >
          <Youtube size={16} />
          Music
        </Button>

        <Button 
          onClick={() => handleFindNearby('gas_station')}
          className="flex items-center gap-2"
          variant="outline"
        >
          <MapPin size={16} />
          Gas Stations
        </Button>

        <Button 
          onClick={() => handleFindNearby('restaurant')}
          className="flex items-center gap-2"
          variant="outline"
        >
          <Coffee size={16} />
          Food & Drinks
        </Button>
      </div>

      <div className="space-y-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Talk to Hadi or Huda..."
          className="w-full p-2 bg-gray-800 text-white rounded border border-gray-600"
        />
        <Button onClick={sendMessage} className="w-full">
          Send Message
        </Button>
      </div>

      {alerts.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Recent Alerts</h4>
          {alerts.map((alert, index) => (
            <div 
              key={index}
              className={`p-2 rounded text-xs ${
                alert.type === 'hadi_alert' 
                  ? 'bg-red-900 text-red-100' 
                  : 'bg-blue-900 text-blue-100'
              }`}
            >
              <strong>{alert.type === 'hadi_alert' ? 'HADI' : 'HUDA'}:</strong> {alert.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}