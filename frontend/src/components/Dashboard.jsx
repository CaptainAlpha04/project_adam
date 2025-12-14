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
                        {[0.5, 0.1, 0.01, 0.002, 0.001].map((speed, idx) => (
                            <button
                                key={speed}
                                onClick={() => fetch(`http://localhost:8000/speed?speed=${speed}`, { method: 'POST' })}
                                className="flex-1 bg-blue-900 hover:bg-blue-800 text-blue-200 border border-blue-600 px-1 py-1 rounded transition-colors uppercase tracking-widest text-[10px] font-bold"
                            >
                                {idx === 0 ? 'Slow' : idx === 1 ? 'Normal' : idx === 2 ? 'Fast' : idx === 3 ? '50x' : '100x'}
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
                                <div className={`w-2 h-2 rounded-full ${agent.needs.hunger > 0.5 ? 'bg-red-500' : 'bg-green-500'}`} title="Hunger"></div>
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
                            <div className="text-sm text-yellow-200/80 italic">
                                {selectedAgent.attributes.gender} • Gen {selectedAgent.attributes.generation}
                            </div>
                            {/* Soul Status Badge */}
                            <div className="flex gap-2 mt-1">
                                <span className={`text-[10px] uppercase font-bold px-1 rounded ${selectedAgent.ruh.karma > 0 ? 'bg-blue-900 text-blue-200' : 'bg-red-900 text-red-200'}`}>
                                    Karma: {selectedAgent.ruh.karma.toFixed(1)}
                                </span>
                                <span className="text-[10px] uppercase font-bold px-1 rounded bg-purple-900 text-purple-200">
                                    Past Lives: {selectedAgent.ruh.past_lives}
                                </span>
                            </div>
                        </div>
                        <button onClick={() => onSelectAgent(null)} className="text-yellow-600 hover:text-yellow-400">✕</button>
                    </div>

                    {/* Content */}
                    <div className="p-4 overflow-y-auto custom-scrollbar space-y-4">

                        {/* TRI-PARTITE STATS */}

                        {/* 1. NAFS (The Beast) */}
                        <div className="border border-red-900/30 rounded p-2 bg-red-900/10">
                            <h3 className="text-red-400 font-bold uppercase text-xs tracking-widest mb-2">Nafs (The Beast)</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <div className="text-xs text-gray-400 uppercase tracking-wider">Health</div>
                                    <div className="h-2 bg-gray-700 rounded mt-1 overflow-hidden">
                                        <div className="h-full bg-red-600" style={{ width: `${selectedAgent.state.health * 100}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs text-gray-400 uppercase tracking-wider">Hunger</div>
                                    <div className="h-2 bg-gray-700 rounded mt-1 overflow-hidden">
                                        <div className="h-full bg-orange-500" style={{ width: `${selectedAgent.nafs.hunger * 100}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs text-gray-400 uppercase tracking-wider">Energy</div>
                                    <div className="h-2 bg-gray-700 rounded mt-1 overflow-hidden">
                                        <div className="h-full bg-yellow-500" style={{ width: `${selectedAgent.nafs.energy * 100}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs text-gray-400 uppercase tracking-wider">Pain</div>
                                    <div className="h-2 bg-gray-700 rounded mt-1 overflow-hidden">
                                        <div className="h-full bg-gray-500" style={{ width: `${selectedAgent.nafs.pain * 100}%` }}></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* 2. QALB (The Heart) */}
                        <div className="border border-green-900/30 rounded p-2 bg-green-900/10">
                            <h3 className="text-green-400 font-bold uppercase text-xs tracking-widest mb-2">Qalb (The Heart)</h3>
                            <div className="grid grid-cols-2 gap-4 mb-2">
                                <div>
                                    <div className="text-xs text-gray-400 uppercase tracking-wider">Happiness</div>
                                    <div className="h-2 bg-gray-700 rounded mt-1 overflow-hidden">
                                        <div className="h-full bg-green-500" style={{ width: `${selectedAgent.state.happiness * 100}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs text-gray-400 uppercase tracking-wider">Social Battery</div>
                                    <div className="h-2 bg-gray-700 rounded mt-1 overflow-hidden">
                                        <div className="h-full bg-blue-500" style={{ width: `${selectedAgent.qalb.social * 100}%` }}></div>
                                    </div>
                                </div>
                            </div>
                            <div className="flex gap-2 text-xs">
                                <div className="bg-green-900/40 p-2 rounded border border-green-700 flex-1">
                                    <span className="text-green-300 uppercase font-bold">Emotion:</span> <span className="text-white ml-2">{selectedAgent.qalb.emotional_state}</span>
                                </div>
                            </div>
                        </div>

                        {/* 3. RUH (The Spirit) */}
                        <div className="border border-purple-900/30 rounded p-2 bg-purple-900/10">
                            <h3 className="text-purple-400 font-bold uppercase text-xs tracking-widest mb-2">Ruh (The Spirit)</h3>
                            <div className="flex gap-2 text-xs">
                                <div className="bg-purple-900/40 p-2 rounded border border-purple-700 flex-1">
                                    <span className="text-purple-300 uppercase font-bold">Life Goal:</span> <span className="text-white ml-2">{selectedAgent.ruh.life_goal}</span>
                                </div>
                                <div className="bg-purple-900/40 p-2 rounded border border-purple-700 flex-1">
                                    <span className="text-purple-300 uppercase font-bold">Wisdom:</span> <span className="text-white ml-2">{selectedAgent.ruh.wisdom.toFixed(2)}</span>
                                </div>
                            </div>
                        </div>

                        {/* 4. Social Hierarchy & State */}
                        <div className="border border-yellow-900/40 rounded p-2 bg-yellow-900/10 mb-2">
                            <h3 className="text-yellow-400 font-bold uppercase text-xs tracking-widest mb-2">Social Status</h3>
                            <div className="text-xs space-y-1">
                                {/* Leader */}
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Leader:</span>
                                    <span className="text-yellow-300">
                                        {selectedAgent.attributes.leader_id ?
                                            (gameState.agents.find(a => a.id === selectedAgent.attributes.leader_id)?.attributes.name || "Unknown")
                                            : "None (Independent)"}
                                    </span>
                                </div>
                                {/* Followers */}
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Followers:</span>
                                    <span className="text-white">{selectedAgent.attributes.followers?.length || 0}</span>
                                </div>
                                {/* Social Lock */}
                                {selectedAgent.state.social_lock_target &&
                                    <div className="bg-blue-900/40 p-1 rounded border border-blue-800 mt-1 flex justify-between items-center animate-pulse">
                                        <span className="text-blue-300">talking to:</span>
                                        <span className="text-white font-bold">
                                            {gameState.agents.find(a => a.id === selectedAgent.state.social_lock_target)?.attributes.name || "Ghost"}
                                        </span>
                                    </div>
                                }
                            </div>
                        </div>

                        {/* Personality Vectors */}
                        <div>
                            <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest border-b border-yellow-900/50 pb-1 mb-2">Personality</h3>
                            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
                                {selectedAgent.attributes.personality_vector && Object.entries(selectedAgent.attributes.personality_vector)
                                    .sort(([, a], [, b]) => b - a) // Sort by value desc
                                    .slice(0, 8) // Top 8
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

                        {/* Actions & Inventory */}
                        <div className="grid grid-cols-2 gap-2">
                            <div>
                                <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest border-b border-yellow-900/50 pb-1 mb-2">Inventory</h3>
                                <div className="flex gap-1 flex-wrap">
                                    {selectedAgent.inventory.length === 0 && <span className="text-gray-500 text-sm italic">Empty</span>}
                                    {selectedAgent.inventory.map((slot, i) => (
                                        <div key={i} className="bg-gray-800 px-2 py-1 rounded border border-gray-600 text-[10px]" title={slot.item.name}>
                                            {slot.item.name} ({slot.count})
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                        <div>
                            <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest border-b border-yellow-900/50 pb-1 mb-2">Opinions</h3>
                            <div className="max-h-20 overflow-y-auto custom-scrollbar text-xs space-y-1">
                                {selectedAgent.qalb.opinions && Object.keys(selectedAgent.qalb.opinions).length > 0 ? (
                                    Object.entries(selectedAgent.qalb.opinions)
                                        .sort(([, a], [, b]) => b - a) // Sort by score deg
                                        .map(([id, score]) => {
                                            const agentName = gameState.agents.find(a => a.id === id)?.attributes.name || "Unknown";
                                            return (
                                                <div key={id} className="flex justify-between">
                                                    <span className="text-gray-400 truncate w-16" title={id}>{agentName}</span>
                                                    <span className={score > 5 ? "text-green-300 font-bold" : score > 0 ? "text-green-500" : score < -5 ? "text-red-500 font-bold" : "text-red-400"}>
                                                        {score.toFixed(2)}
                                                    </span>
                                                </div>
                                            );
                                        })
                                ) : (
                                    <div className="italic text-gray-500">No opinions yet</div>
                                )}
                            </div>
                        </div>

                        {/* Social Brain (Game Theory) */}
                        <div className="mb-2">
                            <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest border-b border-yellow-900/50 pb-1 mb-2">Social Brain</h3>
                            <div className="text-xs space-y-1">
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Strategy:</span>
                                    <span className="text-purple-300 font-bold">{selectedAgent.strategy}</span>
                                </div>
                                <div className="mt-1">
                                    <span className="text-gray-500 text-[10px] uppercase">Memory of Others:</span>
                                    <div className="flex gap-1 flex-wrap mt-1">
                                        {selectedAgent.social_memory && Object.keys(selectedAgent.social_memory).length > 0 ? (
                                            Object.entries(selectedAgent.social_memory).map(([id, move]) => {
                                                const name = gameState.agents.find(a => a.id === id)?.attributes.name || "???";
                                                return (
                                                    <div key={id} className={`px-2 py-0.5 rounded border text-[10px] ${move === 'cooperate' ? 'bg-green-900/30 border-green-700 text-green-300' : 'bg-red-900/30 border-red-700 text-red-300'}`}>
                                                        {name}: {move}
                                                    </div>
                                                )
                                            })
                                        ) : <span className="text-gray-600 italic text-[10px]">Tabula Rasa</span>}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Tribe & Lineage (Politics) */}
                        <div className="mb-2">
                            <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest border-b border-yellow-900/50 pb-1 mb-2">Tribe & Lineage</h3>
                            <div className="grid grid-cols-2 gap-2 text-xs">
                                <div>
                                    <span className="text-gray-500 block text-[10px]">Generation</span>
                                    <span className="text-white font-mono">{selectedAgent.generation}</span>
                                </div>
                                <div>
                                    <span className="text-gray-500 block text-[10px]">Tribe</span>
                                    <span className="text-yellow-300 font-bold">
                                        {selectedAgent.tribe_name || "Nomad"}
                                    </span>
                                    {/* Role */}
                                    <div className="text-[9px] text-gray-400">
                                        {selectedAgent.attributes.leader_id === selectedAgent.id ? "👑 Chief" : (selectedAgent.tribe_id ? "Member" : "Rogue")}
                                    </div>
                                </div>
                                <div className="col-span-2">
                                    <span className="text-gray-500 block text-[10px]">Orders</span>
                                    <span className="text-orange-300 font-mono text-[10px] uppercase">
                                        {selectedAgent.tribe_goal || "Wander"}
                                    </span>
                                </div>

                                <div>
                                    <span className="text-gray-500 block text-[10px]">Leader</span>
                                    <span className="text-gray-300">
                                        {selectedAgent.attributes.leader_id
                                            ? (selectedAgent.attributes.leader_id === selectedAgent.id ? "Self" : gameState.agents.find(a => a.id === selectedAgent.attributes.leader_id)?.attributes.name || "Unknown")
                                            : "None"}
                                    </span>
                                </div>
                                <div>
                                    <span className="text-gray-500 block text-[10px]">Partner</span>
                                    <span className="text-pink-300">
                                        {selectedAgent.attributes.partner_id
                                            ? (gameState.agents.find(a => a.id === selectedAgent.attributes.partner_id)?.attributes.name || "Unknown")
                                            : "-"}
                                    </span>
                                </div>
                                <div className="col-span-2">
                                    <span className="text-gray-500 block text-[10px]">Social Circle</span>
                                    <div className="flex gap-2">
                                        <span className="text-green-400" title="Friends">💚 {selectedAgent.attributes.friend_ids?.length || 0}</span>
                                        <span className="text-red-400" title="Rivals">⚔️ {Object.values(selectedAgent.qalb?.opinions || {}).filter(v => v <= -30).length}</span>
                                        <span className="text-blue-400" title="Followers">👥 {gameState.agents.filter(a => a.attributes.leader_id === selectedAgent.id && a.id !== selectedAgent.id).length}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Perception (New Section) */}
                    <div className="mb-2">
                        <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest border-b border-yellow-900/50 pb-1 mb-2">Visual Perception</h3>
                        <div className="flex gap-1 flex-wrap text-xs">
                            {selectedAgent.visible_agents && selectedAgent.visible_agents.length > 0 ? (
                                selectedAgent.visible_agents.map((name, i) => (
                                    <span key={i} className="bg-blue-900/50 px-2 py-1 rounded border border-blue-700 text-blue-200">
                                        👁 {name}
                                    </span>
                                ))
                            ) : (
                                <span className="text-gray-500 italic">No one in sight</span>
                            )}
                        </div>
                    </div>

                    {/* Recent Diary */}
                    <div>
                        <div className="flex justify-between items-center border-b border-yellow-900/50 pb-1 mb-2">
                            <h3 className="text-yellow-500 font-bold uppercase text-xs tracking-widest">Diary of the Soul</h3>
                        </div>
                        <div className="mt-2 max-h-32 overflow-y-auto text-xs font-mono bg-black/30 p-2 rounded text-gray-400 custom-scrollbar">
                            {selectedAgent.diary && selectedAgent.diary.slice().reverse().map((entry, i) => (
                                <div key={i} className="mb-1">{entry}</div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
};

export default Dashboard;
