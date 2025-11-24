import React, { useState, useEffect } from 'react';
import MapCanvas from './components/MapCanvas';
import Dashboard from './components/Dashboard';

function App() {
  const [gameState, setGameState] = useState(null);
  const [connected, setConnected] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState(null);
  const [ws, setWs] = useState(null);

  useEffect(() => {
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
    };

    return () => {
      socket.close();
    };
  }, []);

  const togglePause = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'pause' }));
    }
  };

  return (
    <div className="flex h-screen bg-gray-900">
      <div className="flex-1 flex justify-center items-center overflow-auto p-4">
        {gameState ? (
          <MapCanvas
            gameState={gameState}
            selectedAgentId={selectedAgentId}
            onSelectAgent={setSelectedAgentId}
          />
        ) : (
          <div className="text-white">Waiting for simulation...</div>
        )}
      </div>
      <Dashboard
        gameState={gameState}
        onTogglePause={togglePause}
        selectedAgentId={selectedAgentId}
        onSelectAgent={setSelectedAgentId}
      />
    </div>
  );
}

export default App;
