import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import Chart from 'chart.js/auto';
import TrainingVisualizer from './TrainingVisualizer';

const socket = io('http://localhost:8000');

const TrainingCenter = () => {
    const [status, setStatus] = useState('idle'); // idle, training
    const [scenario, setScenario] = useState('movement');
    const [stats, setStats] = useState({ step: 0, reward: 0 });
    const [mapData, setMapData] = useState(null);
    const [rewardHistory, setRewardHistory] = useState([]);

    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    useEffect(() => {
        // Socket Listeners
        socket.on('training_update', (data) => {
            setStats({ step: data.step, reward: data.reward });
            setMapData(data.map);

            setRewardHistory(prev => {
                const newHist = [...prev, data.reward];
                if (newHist.length > 50) newHist.shift();
                return newHist;
            });
        });

        return () => {
            socket.off('training_update');
        };
    }, []);

    // Chart Effect
    useEffect(() => {
        if (chartRef.current) {
            if (chartInstance.current) chartInstance.current.destroy();

            chartInstance.current = new Chart(chartRef.current, {
                type: 'line',
                data: {
                    labels: rewardHistory.map((_, i) => i),
                    datasets: [{
                        label: 'Reward',
                        data: rewardHistory,
                        borderColor: '#60a5fa',
                        tension: 0.1
                    }]
                },
                options: {
                    animation: false,
                    responsive: true,
                    scales: { y: { beginAtZero: false } }
                }
            });
        }
    }, [rewardHistory]);

    const startTraining = async () => {
        try {
            const res = await fetch('http://localhost:8000/train/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ scenario, generations: 10 })
            });
            if (res.ok) setStatus('training');
        } catch (err) {
            console.error(err);
        }
    };

    const stopTraining = async () => {
        try {
            await fetch('http://localhost:8000/train/stop', { method: 'POST' });
            setStatus('idle');
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="flex h-screen bg-gray-900 text-white p-6 gap-6">
            {/* Sidebar Controls */}
            <div className="w-1/4 flex flex-col gap-4">
                <h1 className="text-2xl font-bold mb-4 text-purple-400">Training Center</h1>

                <div className="bg-gray-800 p-4 rounded-lg">
                    <label className="block text-sm font-medium mb-2">Scenario</label>
                    <select
                        value={scenario}
                        onChange={(e) => setScenario(e.target.value)}
                        className="w-full bg-gray-700 rounded p-2 border border-gray-600 focus:outline-none focus:border-purple-500"
                        disabled={status === 'training'}
                    >
                        <option value="movement">Movement (Find Food)</option>
                        <option value="crafting">Crafting (Gather & Build)</option>
                        <option value="social">Social (Interaction)</option>
                    </select>
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={startTraining}
                        disabled={status === 'training'}
                        className={`flex-1 py-2 rounded font-bold transition-colors ${status === 'training'
                                ? 'bg-gray-600 cursor-not-allowed'
                                : 'bg-green-600 hover:bg-green-500'
                            }`}
                    >
                        Start Training
                    </button>
                    <button
                        onClick={stopTraining}
                        disabled={status === 'idle'}
                        className={`flex-1 py-2 rounded font-bold transition-colors ${status === 'idle'
                                ? 'bg-gray-600 cursor-not-allowed'
                                : 'bg-red-600 hover:bg-red-500'
                            }`}
                    >
                        Stop
                    </button>
                </div>

                <div className="bg-gray-800 p-4 rounded-lg mt-auto">
                    <h3 className="text-lg font-semibold mb-2">Stats</h3>
                    <div className="flex justify-between">
                        <span className="text-gray-400">Step:</span>
                        <span>{stats.step}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-400">Reward:</span>
                        <span className={stats.reward >= 0 ? 'text-green-400' : 'text-red-400'}>
                            {stats.reward.toFixed(2)}
                        </span>
                    </div>
                </div>
            </div>

            {/* Main Visualizer */}
            <div className="flex-1 flex flex-col gap-6">
                <div className="flex-1 bg-gray-800 rounded-lg p-4 flex items-center justify-center">
                    {mapData ? (
                        <TrainingVisualizer mapData={mapData} />
                    ) : (
                        <div className="text-gray-500">Waiting for training data...</div>
                    )}
                </div>

                {/* Graphs */}
                <div className="h-1/3 bg-gray-800 rounded-lg p-4">
                    <canvas ref={chartRef}></canvas>
                </div>
            </div>
        </div>
    );
};

export default TrainingCenter;
