"use client";
import { useState } from "react";
import { Button } from "@/components/livekit/button";

interface ConnectivityPanelProps {
  onConnect: (type: string, data: any) => void;
}

export function ConnectivityPanel({ onConnect }: ConnectivityPanelProps) {
  const [activeTab, setActiveTab] = useState("wifi");

  return (
    <div className="p-4 bg-gray-100 rounded-lg">
      <div className="flex space-x-2 mb-4">
        {["wifi", "bluetooth", "youtube", "maps"].map((tab) => (
          <Button
            key={tab}
            onClick={() => setActiveTab(tab)}
            variant={activeTab === tab ? "default" : "outline"}
          >
            {tab.toUpperCase()}
          </Button>
        ))}
      </div>

      {activeTab === "wifi" && (
        <div>
          <Button onClick={() => onConnect("wifi_scan", {})}>
            Scan WiFi
          </Button>
        </div>
      )}

      {activeTab === "bluetooth" && (
        <div>
          <Button onClick={() => onConnect("bluetooth_scan", {})}>
            Scan Bluetooth
          </Button>
        </div>
      )}

      {activeTab === "youtube" && (
        <div>
          <input
            type="text"
            placeholder="Search music..."
            className="p-2 border rounded mr-2"
            onKeyPress={(e) => {
              if (e.key === "Enter") {
                onConnect("youtube_search", { query: e.currentTarget.value });
              }
            }}
          />
        </div>
      )}

      {activeTab === "maps" && (
        <div>
          <Button onClick={() => onConnect("maps_nearby", { type: "gas_station" })}>
            Find Gas Stations
          </Button>
        </div>
      )}
    </div>
  );
}