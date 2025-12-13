import React, { useState, useEffect } from 'react';
import MapCanvas from './components/MapCanvas';
import Dashboard from './components/Dashboard';
import TrainingCenter from './components/Training/TrainingCenter';

function App() {
  const [view, setView] = useState('simulation'); // simulation, training
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
    <div className="flex flex-col h-screen bg-gray-900">
      {/* Navigation */}
      <div className="bg-gray-800 p-4 flex gap-4 border-b border-gray-700">
        <h1 className="text-xl font-bold text-white mr-8">Project Adam</h1>
        <button
          onClick={() => setView('simulation')}
          className={`px-4 py-2 rounded font-semibold ${view === 'simulation' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'}`}
        >
          Simulation
        </button>
        <button
          onClick={() => setView('training')}
          className={`px-4 py-2 rounded font-semibold ${view === 'training' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'}`}
        >
          Training Center
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden relative">
        {view === 'simulation' ? (
          <div className="flex h-full">
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
        ) : (
          <TrainingCenter />
        )}
      </div>
    </div>
  );
}

export default App;
