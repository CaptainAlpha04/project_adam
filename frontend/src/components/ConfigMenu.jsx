import React, { useState } from 'react';

const ConfigMenu = ({ onStart }) => {
    const [config, setConfig] = useState({
        hunger_rate: 0.002,
        resource_growth_rate: 1.0,
        initial_agent_count: 50
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setConfig(prev => ({
            ...prev,
            [name]: parseFloat(value)
        }));
    };

    const handleSubmit = async () => {
        try {
            console.log("Initializing World with...", config);
            const res = await fetch('http://localhost:8000/init_world', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            if (res.ok) {
                const data = await res.json();
                console.log("World Initialized:", data);
                onStart();
            } else {
                console.error("Failed to init world");
            }
        } catch (e) {
            console.error("Error connecting to backend:", e);
        }
    };

    return (
        <div className="w-full h-full flex flex-col items-center justify-center bg-stone-900 text-yellow-100 font-serif">
            <h1 className="text-4xl font-bold mb-8 text-yellow-500 uppercase tracking-widest drop-shadow-md">Project Adam</h1>
            <div className="bg-stone-800 p-8 rounded-lg border-2 border-yellow-700 shadow-2xl w-96 flex flex-col gap-6">

                {/* Agent Count */}
                <div className="flex flex-col gap-2">
                    <label className="text-sm uppercase font-bold text-stone-500 tracking-wider">Initial Agents: {config.initial_agent_count}</label>
                    <input
                        type="range"
                        name="initial_agent_count"
                        min="2" max="100"
                        value={config.initial_agent_count}
                        onChange={handleChange}
                        className="accent-yellow-500 cursor-pointer"
                    />
                </div>

                {/* Hunger Rate */}
                <div className="flex flex-col gap-2">
                    <label className="text-sm uppercase font-bold text-stone-500 tracking-wider">Hunger Rate: {config.hunger_rate}</label>
                    <input
                        type="range"
                        name="hunger_rate"
                        min="0.0005" max="0.01" step="0.0005"
                        value={config.hunger_rate}
                        onChange={handleChange}
                        className="accent-red-500 cursor-pointer"
                    />
                    <span className="text-xs text-stone-600 italic">
                        {config.hunger_rate < 0.002 ? "Slow Starvation" : config.hunger_rate > 0.005 ? "Brutal Survival" : "Standard"}
                    </span>
                </div>

                {/* Resource Growth */}
                <div className="flex flex-col gap-2">
                    <label className="text-sm uppercase font-bold text-stone-500 tracking-wider">Resource Growth: {config.resource_growth_rate}x</label>
                    <input
                        type="range"
                        name="resource_growth_rate"
                        min="0.1" max="5.0" step="0.1"
                        value={config.resource_growth_rate}
                        onChange={handleChange}
                        className="accent-green-500 cursor-pointer"
                    />
                    <span className="text-xs text-stone-600 italic">
                        {config.resource_growth_rate < 1.0 ? "Scarcity" : config.resource_growth_rate > 2.0 ? "Abundance" : "Standard"}
                    </span>
                </div>

                <button
                    onClick={handleSubmit}
                    className="mt-4 bg-yellow-700 hover:bg-yellow-600 text-stone-900 font-bold py-3 rounded border border-yellow-500 uppercase tracking-widest transition-all shadow-lg active:scale-95"
                >
                    Initialize Simulation
                </button>
            </div>

            <p className="mt-8 text-stone-600 text-xs italic">"And the Lord God formed man of the dust of the ground..."</p>
        </div>
    );
};

export default ConfigMenu;
