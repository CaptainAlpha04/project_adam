import React, { useState, useEffect } from 'react';
import MapCanvas from './components/MapCanvas';
import Dashboard from './components/Dashboard';
import TrainingCenter from './components/Training/TrainingCenter';

function App() {
  const [view, setView] = useState('simulation'); // simulation as default
  const [gameState, setGameState] = useState(null);
  const [connected, setConnected] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState(null);
  const [mapMode, setMapMode] = useState('TERRAIN');
  const [ws, setWs] = useState(null);

  useEffect(() => {
    // Reconnection logic could be added here
    const connect = () => {
      const socket = new WebSocket('ws://localhost:8000/ws');
      setWs(socket);

      socket.onopen = () => {
        console.log('Connected to backend');
        setConnected(true);
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setGameState(data);
      };

      socket.onclose = () => {
        console.log('Disconnected');
        setConnected(false);
        // setTimeout(connect, 3000); // Auto-reconnect
      };
      return socket;
    }
    const socket = connect();
    return () => socket.close();
  }, []);

  const togglePause = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'pause' }));
    }
  };

  return (
    <div className="w-full h-screen bg-black overflow-hidden relative">
      {view === 'simulation' ? (
        <>
          {/* Layer 1: The World (Canvas) */}
          <div className="absolute inset-0 z-0">
            <MapCanvas
              gameState={gameState}
              selectedAgentId={selectedAgentId}
              onSelectAgent={setSelectedAgentId}
              mapMode={mapMode}
            />
          </div>

          {/* Layer 2: The HUD (Dashboard) */}
          <div className="absolute inset-0 z-10 pointer-events-none">
            <Dashboard
              gameState={gameState}
              selectedAgentId={selectedAgentId}
              onSelectAgent={setSelectedAgentId}
              onTogglePause={togglePause}
              mapMode={mapMode}
              setMapMode={setMapMode}
            />

            {/* Temp Navigation to Training (Hidden/Integrated) */}
            <div className="pointer-events-auto absolute bottom-4 left-4 z-50">
              <button
                onClick={() => setView('training')}
                className="bg-stone-800 text-stone-500 hover:text-white px-2 py-1 text-xs border border-stone-600 rounded opacity-50 hover:opacity-100 transition-opacity"
              >
                Go to Training
              </button>
            </div>
          </div>
        </>
      ) : (
        <div className="relative w-full h-full bg-stone-900 overflow-auto">
          <button
            onClick={() => setView('simulation')}
            className="absolute top-4 left-4 z-50 bg-stone-700 text-white px-4 py-2 rounded shadow border border-stone-500 hover:bg-stone-600"
          >
            ← Back to World
          </button>
          <TrainingCenter />
        </div>
      )}

      {/* Loading / Connection State Overlay */}
      {!connected && (
        <div className="absolute inset-0 z-[100] bg-black/80 flex items-center justify-center pointer-events-none">
          <div className="text-yellow-500 font-serif text-2xl animate-pulse">
            Connecting to the Matrix...
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
