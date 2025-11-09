'use client';

import { RoomAudioRenderer, StartAudio } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { SessionProvider } from '@/components/app/session-provider';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/livekit/toaster';
import { HadiHudaControls } from '@/components/app/hadi-huda-controls';

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  return (
    <SessionProvider appConfig={appConfig}>
      <div className="flex h-svh">
        <main className="flex-1 grid place-content-center">
          <ViewController />
        </main>
        <aside className="w-80 p-4 bg-gray-950 border-l border-gray-800">
          <HadiHudaControls />
        </aside>
      </div>
      <StartAudio label="Start Audio" />
      <RoomAudioRenderer />
      <Toaster />
    </SessionProvider>
  );
}
