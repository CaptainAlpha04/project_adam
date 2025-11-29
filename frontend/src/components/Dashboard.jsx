import React, { useState } from 'react';

const Dashboard = ({ gameState, onSelectAgent, selectedAgentId }) => {
    const [showDetails, setShowDetails] = useState(false);

    if (!gameState) return <div className="text-white p-4">Loading...</div>;

    // Find selected agent
    const selectedAgent = gameState.agents.find(a => a.id === selectedAgentId);

    return (
        <div className="absolute top-0 left-0 p-4 w-full h-full pointer-events-none flex flex-col justify-between">
            {/* Top Bar */}
            <div className="pointer-events-auto flex justify-between items-start">
                <div className="bg-gray-900/90 p-4 rounded-lg border-2 border-yellow-600 shadow-xl backdrop-blur-sm text-yellow-100 font-serif max-w-md">
                    <h1 className="text-3xl font-bold mb-2 text-yellow-500 tracking-wider uppercase border-b border-yellow-700 pb-1">Project Adam</h1>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
                        <div><span className="text-gray-400">Time Step:</span> <span className="font-mono text-yellow-200">{gameState.time_step}</span></div>
                        <div><span className="text-gray-400">Agents:</span> <span className="font-mono text-yellow-200">{gameState.agents.length}</span></div>
                        <div><span className="text-gray-400">Animals:</span> <span className="font-mono text-yellow-200">{gameState.animals.length}</span></div>
                        <div><span className="text-gray-400">Gen:</span> <span className="font-mono text-yellow-200">{gameState.generation}</span></div>
                        <div><span className="text-gray-400">Status:</span> <span className={`font-bold ${gameState.paused ? 'text-red-400' : 'text-green-400'}`}>{gameState.paused ? 'PAUSED' : 'RUNNING'}</span></div>
                    </div>

                    {/* Pause Button */}
                    {/* Pause Button */}
                    <button
                        onClick={() => {
                            const ws = new WebSocket('ws://localhost:8000/ws');
                            ws.onopen = () => {
                                ws.send(JSON.stringify({ type: 'pause' }));
                                ws.close();
                            };
                        }}
                        className="mt-3 w-full bg-yellow-900 hover:bg-yellow-800 text-yellow-200 border border-yellow-600 px-3 py-1 rounded transition-colors uppercase tracking-widest text-xs font-bold"
                    >
                        {gameState.paused ? 'Resume Simulation' : 'Pause Simulation'}
                    </button>

                    {/* Speed Controls */}
                    <div className="mt-2 flex gap-1">
                        {[0.5, 0.1, 0.01].map((speed, idx) => (
                            <button
                                key={speed}
                                onClick={() => fetch(`http://localhost:8000/speed?speed=${speed}`, { method: 'POST' })}
                                className="flex-1 bg-blue-900 hover:bg-blue-800 text-blue-200 border border-blue-600 px-1 py-1 rounded transition-colors uppercase tracking-widest text-[10px] font-bold"
                            >
                                {idx === 0 ? 'Slow' : idx === 1 ? 'Normal' : 'Fast'}
                            </button>
                        ))}
                    </div>

                    <button
                        onClick={() => fetch('http://localhost:8000/evolve', { method: 'POST' })}
                        className="mt-2 w-full bg-purple-900 hover:bg-purple-800 text-purple-200 border border-purple-600 px-3 py-1 rounded transition-colors uppercase tracking-widest text-xs font-bold"
                    >
                        Force Evolution
                    </button>
                </div>

                {/* Agent List (Right Side) */}
                <div className="bg-gray-900/80 p-2 rounded-lg border border-gray-700 max-h-96 overflow-y-auto pointer-events-auto">
                    <h3 className="text-xs font-bold text-gray-400 uppercase mb-2 px-2">Agents</h3>
                    {gameState.agents.map(agent => (
                        <div
                            key={agent.id}
                            onClick={() => onSelectAgent(agent.id)}
                            className={`cursor-pointer px-3 py-1 rounded text-sm mb-1 transition-colors flex justify-between items-center gap-4 ${selectedAgentId === agent.id ? 'bg-yellow-900/50 text-yellow-200 border border-yellow-700' : 'text-gray-300 hover:bg-gray-800'}`}
                        >
                            <span>{agent.attributes.name}</span>
                            <div className="flex gap-1">
                                <div className={`w-2 h-2 rounded-full ${agent.state.hunger > 0.5 ? 'bg-red-500' : 'bg-green-500'}`} title="Hunger"></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Character Detail Pane (CK3 Style) */}
            {selectedAgent && (
                <div className="pointer-events-auto absolute bottom-4 left-4 bg-gray-900/95 border-2 border-yellow-600 rounded-lg shadow-2xl w-[500px] max-h-[80vh] overflow-hidden flex flex-col text-yellow-100 font-serif">
                    {/* Header */}
                    <div className="bg-gradient-to-r from-yellow-900/50 to-gray-900 p-4 border-b border-yellow-700 flex justify-between items-start">
                        <div>
                            <h2 className="text-2xl font-bold text-yellow-400">{selectedAgent.attributes.name}</h2>
                            <div className="text-sm text-yellow-200/80 italic">{selectedAgent.attributes.gender} • Gen {selectedAgent.attributes.generation} • {selectedAgent.traits ? selectedAgent.traits.join(", ") : "Unknown"}</div>
                        </div>
                        <button onClick={() => onSelectAgent(null)} className="text-yellow-600 hover:text-yellow-400">✕</button>
                    </div>

                    {/* Content */}
                    <div className="p-4 overflow-y-auto custom-scrollbar space-y-4">

                        {/* Stats Grid */}
                        <div className="grid grid-cols-2 gap-4 bg-black/20 p-3 rounded border border-yellow-900/30">
                            <div>
                                <div className="text-xs text-gray-400 uppercase tracking-wider">Health</div>
                                <div className="h-2 bg-gray-700 rounded mt-1 overflow-hidden">
                                    <div className="h-full bg-red-600" style={{ width: `${selectedAgent.state.health * 100}%` }}></div>
                                </div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-400 uppercase tracking-wider">Happiness</div>
                                <div className="h-2 bg-gray-700 rounded mt-1 overflow-hidden">
                                    <div className="h-full bg-green-500" style={{ width: `${selectedAgent.state.happiness * 100}%` }}></div>
                                </div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-400 uppercase tracking-wider">Hunger</div>
                                <div className="h-2 bg-gray-700 rounded mt-1 overflow-hidden">
                                    <div className="h-full bg-orange-500" style={{ width: `${selectedAgent.state.hunger * 100}%` }}></div>
                                </div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-400 uppercase tracking-wider">Thirst</div>
                                <div className="h-2 bg-gray-700 rounded mt-1 overflow-hidden">
                                    <div className="h-full bg-blue-500" style={{ width: `${selectedAgent.state.thirst * 100}%` }}></div>
                                </div>
                            </div>
                        </div>

                        {/* Goals */}
                        <div className="space-y-2">
                            <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest border-b border-yellow-900/50 pb-1">Current Objectives</h3>
                            <div className="grid grid-cols-3 gap-2">
                                <div className="bg-yellow-900/20 p-2 rounded border border-yellow-900/30">
                                    <div className="text-[10px] text-red-400 uppercase">Immediate</div>
                                    <div className="font-bold text-yellow-100 text-xs">{selectedAgent.immediate_goal || "None"}</div>
                                </div>
                                <div className="bg-yellow-900/20 p-2 rounded border border-yellow-900/30">
                                    <div className="text-[10px] text-yellow-600 uppercase">Short Term</div>
                                    <div className="font-bold text-yellow-100 text-xs">{selectedAgent.short_term_goal || "None"}</div>
                                </div>
                                <div className="bg-yellow-900/20 p-2 rounded border border-yellow-900/30">
                                    <div className="text-[10px] text-blue-400 uppercase">Long Term</div>
                                    <div className="font-bold text-yellow-100 text-xs">{selectedAgent.long_term_goal || "None"}</div>
                                </div>
                            </div>
                        </div>

                        {/* Personality Vectors */}
                        <div>
                            <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest border-b border-yellow-900/50 pb-1 mb-2">Personality Vectors</h3>
                            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
                                {selectedAgent.attributes.personality_vector && Object.entries(selectedAgent.attributes.personality_vector)
                                    .sort(([, a], [, b]) => b - a) // Sort by value desc
                                    .slice(0, 10) // Top 10
                                    .map(([trait, val]) => (
                                        <div key={trait} className="flex justify-between items-center">
                                            <span className="text-gray-400">{trait}</span>
                                            <div className="w-16 h-1.5 bg-gray-800 rounded overflow-hidden">
                                                <div className="h-full bg-purple-500" style={{ width: `${val * 100}%` }}></div>
                                            </div>
                                        </div>
                                    ))}
                            </div>
                        </div>

                        {/* Opinions */}
                        <div>
                            <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest border-b border-yellow-900/50 pb-1 mb-2">Opinions</h3>
                            <div className="max-h-20 overflow-y-auto custom-scrollbar text-xs space-y-1">
                                {selectedAgent.opinions && Object.keys(selectedAgent.opinions).length > 0 ? (
                                    Object.entries(selectedAgent.opinions).map(([id, score]) => {
                                        const agentName = gameState.agents.find(a => a.id === id)?.attributes.name || "Unknown";
                                        return (
                                            <div key={id} className="flex justify-between">
                                                <span className="text-gray-400 truncate w-24" title={id}>{agentName}</span>
                                                <span className={score > 0 ? "text-green-400" : "text-red-400"}>{score.toFixed(2)}</span>
                                            </div>
                                        );
                                    })
                                ) : (
                                    <div className="italic text-gray-500">No strong opinions yet.</div>
                                )}
                            </div>
                        </div>

                        {/* Inventory */}
                        <div>
                            <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest border-b border-yellow-900/50 pb-1 mb-2">Inventory</h3>
                            <div className="flex gap-2 flex-wrap">
                                {selectedAgent.inventory.length === 0 && <span className="text-gray-500 text-sm italic">Empty</span>}
                                {selectedAgent.inventory.map((slot, i) => (
                                    <div key={i} className="bg-gray-800 px-2 py-1 rounded border border-gray-600 text-xs flex items-center gap-2" title={slot.item.tags.join(", ")}>
                                        <span className="text-gray-300">{slot.item.name}</span>
                                        <span className="bg-gray-700 text-white px-1 rounded text-[10px]">{slot.count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Memory / Diary */}
                        <div>
                            <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest border-b border-yellow-900/50 pb-1 mb-2">Recent Memories</h3>
                            <div className="space-y-1 max-h-32 overflow-y-auto text-sm text-gray-300 custom-scrollbar">
                                {selectedAgent.memory && selectedAgent.memory.length > 0 ? (
                                    selectedAgent.memory.slice().reverse().map((mem, i) => (
                                        <div key={i} className="border-l-2 border-gray-700 pl-2 py-0.5">
                                            <span className="text-yellow-500 font-bold">[{mem.type}]</span> {mem.description}
                                        </div>
                                    ))
                                ) : (
                                    <div className="italic text-gray-500">No memories yet...</div>
                                )}
                            </div>
                        </div>

                        {/* Full Diary Link/Toggle */}
                        <div className="pt-2 border-t border-yellow-900/30">
                            <details>
                                <summary className="cursor-pointer text-xs text-yellow-600 hover:text-yellow-400 uppercase font-bold select-none">View Full Diary Log</summary>
                                <div className="mt-2 max-h-40 overflow-y-auto text-xs font-mono bg-black/30 p-2 rounded text-gray-400 custom-scrollbar">
                                    {selectedAgent.diary.slice().reverse().map((entry, i) => (
                                        <div key={i}>{entry}</div>
                                    ))}
                                </div>
                            </details>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
