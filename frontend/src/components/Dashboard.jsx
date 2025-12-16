import React, { useState, useEffect, useMemo, useRef } from 'react';

// --- SUB-COMPONENTS (Lifted out to preserve state) ---

const TopBar = React.memo(({ gameState, onTogglePause }) => {
    return (
        <div className="pointer-events-auto absolute top-0 left-0 w-full h-16 bg-stone-900 border-b-4 border-yellow-900 shadow-xl flex justify-between items-center px-6 z-50">
            {/* Title & Date */}
            <div className="flex items-center gap-6">
                <h1 className="text-2xl font-serif font-bold text-yellow-500 uppercase tracking-widest drop-shadow-md">Project Adam</h1>
                <div className="flex flex-col border-l border-stone-700 pl-6">
                    <span className="text-xs text-stone-400 uppercase tracking-wide">Date</span>
                    <span className="text-yellow-100 font-mono text-lg font-bold">{gameState.date || `Steps: ${gameState.time_step}`}</span>
                </div>
            </div>

            {/* Global Resources */}
            <div className="flex gap-8">
                <ResourceItem label="Population" value={gameState.agents.length} icon="👥" color="text-blue-400" />
                <ResourceItem label="Generations" value={gameState.generation} icon="🧬" color="text-purple-400" />
                <ResourceItem label="Prophets" value={gameState.agents.filter(a => a.attributes.is_prophet).length} icon="🔮" color="text-pink-400" />
                <ResourceItem label="Harmony" value="56%" icon="⚖️" color="text-green-400" />
            </div>

            {/* Controls */}
            <div className="flex items-center gap-4">
                <button
                    onClick={onTogglePause}
                    className={`px-6 py-1 rounded border-2 font-bold uppercase tracking-wider text-sm transition-all ${gameState.paused
                        ? 'bg-yellow-600 border-yellow-400 text-stone-900 hover:bg-yellow-500'
                        : 'bg-stone-800 border-stone-600 text-stone-400 hover:bg-stone-700'
                        }`}
                >
                    {gameState.paused ? 'Play' : 'Pause'}
                </button>
                <div className="flex gap-1 border-l border-stone-700 pl-4">
                    {['0.1', '1.0', '5.0'].map((spd, i) => (
                        <button key={i} onClick={() => fetch(`http://localhost:8000/speed?speed=${spd === '5.0' ? 0.001 : spd === '1.0' ? 0.1 : 0.5}`, { method: 'POST' })} className="w-8 h-8 rounded bg-stone-800 text-stone-500 hover:text-yellow-500 border border-stone-700 flex items-center justify-center font-bold">
                            {i + 1}x
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
});

const ResourceItem = ({ label, value, icon, color }) => (
    <div className="flex items-center gap-3" title={label}>
        <span className="text-2xl">{icon}</span>
        <div className="flex flex-col">
            <span className={`font-bold font-mono text-lg leading-none ${color}`}>{value}</span>
            <span className="text-[10px] text-stone-500 uppercase font-bold tracking-wider">{label}</span>
        </div>
    </div>
);

const MapModeSelector = React.memo(({ mapMode, setMapMode }) => (
    <div className="pointer-events-auto absolute bottom-6 right-6 flex flex-col gap-2 bg-stone-900/90 p-2 rounded border border-yellow-900/50 shadow-lg backdrop-blur z-50">
        <span className="text-[10px] uppercase text-stone-500 font-bold text-center mb-1">Map Mode</span>
        {['TERRAIN', 'POLITICAL', 'RELIGIOUS'].map(mode => (
            <button
                key={mode}
                onClick={() => setMapMode && setMapMode(mode)}
                className={`w-32 py-1 text-xs font-bold uppercase tracking-wider border rounded transition-all ${mapMode === mode
                    ? 'bg-yellow-900/80 border-yellow-500 text-yellow-100'
                    : 'bg-stone-800 border-stone-700 text-stone-500 hover:bg-stone-700'
                    }`}
            >
                {mode}
            </button>
        ))}
    </div>
));

const AgentList = React.memo(({ agents, selectedAgentId, onSelectAgent }) => {
    return (
        <div className="pointer-events-auto absolute top-20 right-4 w-64 max-h-[40vh] bg-stone-900/95 border border-stone-700 rounded shadow-xl flex flex-col backdrop-blur-sm z-40">
            <div className="p-2 border-b border-stone-800 bg-stone-900 rounded-t flex justify-between items-center">
                <h3 className="text-xs font-bold text-stone-400 uppercase tracking-widest">Census</h3>
                <span className="bg-stone-800 px-2 rounded text-[10px] text-stone-500">{agents.length}</span>
            </div>
            <div className="overflow-y-auto custom-scrollbar p-2 space-y-1">
                {agents.map(agent => (
                    <div
                        key={agent.id}
                        onClick={() => onSelectAgent(agent.id)}
                        className={`cursor-pointer px-2 py-1 rounded border flex justify-between items-center transition-all ${selectedAgentId === agent.id
                            ? 'bg-yellow-900/40 border-yellow-600/50 text-yellow-200'
                            : 'bg-stone-800/50 border-transparent text-stone-400 hover:bg-stone-800 hover:text-stone-200'
                            }`}
                    >
                        <span className="text-xs font-bold truncate w-32">{agent.attributes.name}</span>
                        <div className="flex gap-1">
                            {agent.attributes.is_prophet && <span title="Prophet">🔮</span>}
                            <div className={`w-2 h-2 rounded-full ${agent.state.health > 0.5 ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
});

const CharacterSheet = React.memo(({ agent, gameState, onSelectAgent, agentMap }) => {
    if (!agent) return null;
    const [tab, setTab] = useState('overview'); // overview, social, inventory

    // Calculate Social Stats
    const socialStats = useMemo(() => {
        const opinions = Object.entries(agent.qalb.opinions);
        const friends = opinions.filter(([, v]) => v > 15).length;
        const enemies = opinions.filter(([, v]) => v < -15).length;
        const followers = agent.attributes.followers ? agent.attributes.followers.length : 0;
        return { friends, enemies, followers };
    }, [agent]);

    return (
        <div className="pointer-events-auto absolute top-20 left-4 w-[510px] max-h-[85vh] bg-stone-900 border-2 border-yellow-700 rounded-lg shadow-2xl flex flex-col z-40 overflow-hidden">
            {/* Header Portrait Area */}
            <div className="h-36 bg-gradient-to-b from-stone-800 to-stone-900 relative border-b border-yellow-800 shrink-0">
                <div className="absolute top-4 left-4 w-24 h-24 bg-stone-800 border-2 border-yellow-600 rounded-full flex items-center justify-center shadow-lg overflow-hidden">
                    <span className="text-5xl">{agent.attributes.gender === 'male' ? '🧔' : '👩'}</span>
                </div>
                <div className="absolute top-4 left-32 right-4">
                    <div className="flex justify-between items-start">
                        <h2 className="text-2xl font-serif font-bold text-yellow-100 drop-shadow-md truncate">{agent.attributes.name}</h2>
                        <span className="text-xs font-bold text-stone-500 uppercase tracking-widest bg-stone-950 px-2 mx-4 py-1 rounded border border-stone-800">
                            {agent.attributes.job || "Gatherer"}
                        </span>
                    </div>
                    <div className="text-sm text-yellow-400/80 font-serif italic mb-1">{agent.tribe_name || "House of Adam"}</div>

                    <div className="flex flex-wrap gap-2 mt-2">
                        <Badge label="Age" value={agent.state.age_steps || '?'} color="bg-stone-700 text-stone-300" />
                        <Badge label="Karma" value={agent.ruh.karma.toFixed(0)} color={agent.ruh.karma > 0 ? "bg-blue-900 text-blue-200" : "bg-red-900 text-red-200"} />
                        <Badge label="Gen" value={agent.generation} color="bg-purple-900 text-purple-200" />
                    </div>
                </div>
                <button onClick={() => onSelectAgent(null)} className="absolute top-2 right-1 text-stone-500 hover:text-red-400 font-bold p-2">✕</button>

                {/* Tabs */}
                <div className="absolute bottom-0 left-0 w-full flex bg-stone-950/50">
                    {['overview', 'social', 'inventory'].map(t => (
                        <button
                            key={t}
                            onClick={() => setTab(t)}
                            className={`flex-1 py-1 text-xs uppercase font-bold tracking-wider transition-colors ${tab === t ? 'bg-yellow-900/40 text-yellow-200 border-t-2 border-yellow-500' : 'text-stone-500 hover:text-stone-300 hover:bg-stone-800'}`}
                        >
                            {t}
                        </button>
                    ))}
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-4 bg-stone-900/95">

                {/* OVERVIEW TAB */}
                {tab === 'overview' && (
                    <>
                        {/* Status Bars */}
                        <div className="space-y-2 bg-stone-800/30 p-2 rounded border border-stone-800">
                            <StatusBar label="Health" value={agent.state.health} color="bg-red-600" />
                            <StatusBar label="Hunger" value={agent.nafs.hunger} color="bg-orange-500" />
                            <StatusBar label="Social Battery" value={agent.qalb.social} color="bg-blue-500" />
                            <StatusBar label="Happiness" value={agent.state.happiness} color="bg-green-500" />
                        </div>

                        {/* Attributes / Personality */}
                        <div>
                            <SectionHeader title="Personality & Beliefs" />
                            <div className="grid grid-cols-2 gap-2">
                                <div className="flex flex-col gap-1">
                                    <span className="text-[10px] text-stone-500 uppercase">Personality</span>
                                    <div className="flex flex-wrap gap-1">
                                        {Object.entries(agent.attributes.personality_vector)
                                            .sort(([, a], [, b]) => b - a)
                                            .slice(0, 6)
                                            .map(([t, v]) => (
                                                <span key={t} className="px-1.5 py-0.5 bg-stone-800 border border-stone-600 rounded text-[10px] text-yellow-100/80">
                                                    {t} {(v * 10).toFixed(0)}
                                                </span>
                                            ))
                                        }
                                    </div>
                                </div>
                                <div className="flex flex-col gap-1">
                                    <span className="text-[10px] text-stone-500 uppercase">Values</span>
                                    <div className="text-xs text-stone-300">
                                        <div>Goal: <span className="text-purple-300">{agent.ruh.life_goal}</span></div>
                                        <div>Strategy: <span className="text-blue-300">{agent.strategy}</span></div>
                                        <div>Wisdom: <span className="text-stone-300">{agent.ruh.wisdom.toFixed(2)}</span></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Chronicle */}
                        <div>
                            <SectionHeader title="Chronicle" />
                            <div className="bg-black/40 p-3 rounded border border-stone-800 text-xs font-mono text-stone-400 max-h-40 overflow-y-auto custom-scrollbar">
                                {agent.diary && agent.diary.slice().reverse().map((entry, i) => (
                                    <div key={i} className="mb-2 border-b border-stone-800/50 pb-1 last:border-0 pl-2 border-l-2 border-stone-700">
                                        <span className="text-yellow-700 mr-2">➜</span>{entry}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </>
                )}

                {/* SOCIAL TAB */}
                {tab === 'social' && (
                    <div className="space-y-4">
                        {/* Social Overview */}
                        <div className="grid grid-cols-3 gap-2 bg-stone-800/20 p-2 rounded">
                            <div className="flex flex-col items-center">
                                <span className="text-xl font-bold text-green-400">{socialStats.friends}</span>
                                <span className="text-[9px] uppercase text-stone-500">Friends</span>
                            </div>
                            <div className="flex flex-col items-center border-l border-stone-800">
                                <span className="text-xl font-bold text-blue-400">{socialStats.followers}</span>
                                <span className="text-[9px] uppercase text-stone-500">Followers</span>
                            </div>
                            <div className="flex flex-col items-center border-l border-stone-800">
                                <span className="text-xl font-bold text-red-400">{socialStats.enemies}</span>
                                <span className="text-[9px] uppercase text-stone-500">Enemies</span>
                            </div>
                        </div>

                        {/* Family */}
                        <div>
                            <SectionHeader title="Lineage" />
                            <div className="grid grid-cols-2 gap-2">
                                <RelationList title="Parents" ids={agent.attributes.parents} names={agent.attributes.parent_names} agentMap={agentMap} onSelect={onSelectAgent} empty="Unknown" />
                                <RelationList title="Children" ids={agent.attributes.children} names={agent.attributes.child_names} agentMap={agentMap} onSelect={onSelectAgent} empty="None" />
                            </div>
                        </div>

                        {/* Hierarchy */}
                        <div>
                            <SectionHeader title="Allegiance" />
                            <div className="grid grid-cols-2 gap-4">
                                <RelationBox title="Partner" id={agent.attributes.partner_id} name={agent.attributes.partner_name} agentMap={agentMap} onSelect={onSelectAgent} />
                                <RelationBox title="Liege Lord" id={agent.attributes.leader_id} name={agent.attributes.leader_name} agentMap={agentMap} onSelect={onSelectAgent} />
                            </div>
                            {agent.attributes.followers && agent.attributes.followers.length > 0 && (
                                <div className="mt-2">
                                    <span className="text-[10px] text-stone-500 uppercase block mb-1">Followers ({agent.attributes.followers.length})</span>
                                    <div className="flex flex-wrap gap-1">
                                        {agent.attributes.followers.map(fid => {
                                            const f = agentMap[fid];
                                            return (
                                                <button
                                                    key={fid}
                                                    onClick={() => onSelectAgent(fid)}
                                                    className="text-xs bg-stone-800 text-blue-200 px-1 rounded hover:bg-stone-700 hover:text-white transition-colors"
                                                >
                                                    {f ? f.attributes.name : 'Unknown'}
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Opinions */}
                        <div>
                            <SectionHeader title="Opinions of Peers" />
                            <div className="space-y-1 max-h-60 overflow-y-auto custom-scrollbar pr-1">
                                {Object.entries(agent.qalb.opinions)
                                    .sort(([, a], [, b]) => b - a)
                                    .map(([id, score]) => {
                                        const target = agentMap[id];
                                        if (!target) return null;
                                        return (
                                            <button
                                                key={id}
                                                onClick={() => onSelectAgent(id)}
                                                className="w-full flex justify-between items-center bg-stone-800/40 px-2 py-1 rounded hover:bg-stone-700 transition-colors text-left group"
                                            >
                                                <div className="flex flex-col">
                                                    <span className="text-xs font-bold text-stone-300 group-hover:text-yellow-200 transition-colors">{target.attributes.name}</span>
                                                    {/* Relationship Tag */}
                                                    <span className="text-[9px] text-stone-500 uppercase">
                                                        {score > 50 ? "Lover" : score > 20 ? "Friend" : score < -20 ? "Rival" : "Acquaintance"}
                                                    </span>
                                                </div>
                                                <div className={`font-mono font-bold text-sm ${score > 0 ? "text-green-500" : "text-red-500"}`}>
                                                    {score.toFixed(0)}
                                                </div>
                                            </button>
                                        )
                                    })
                                }
                                {Object.keys(agent.qalb.opinions).length === 0 && <span className="text-xs text-stone-500 italic">No opinions formed.</span>}
                            </div>
                        </div>
                    </div>
                )}

                {/* INVENTORY TAB */}
                {tab === 'inventory' && (
                    <div className="space-y-4">
                        <div>
                            <SectionHeader title="Possessions" />
                            <div className="grid grid-cols-4 gap-2">
                                {agent.inventory.map((slot, i) => (
                                    <div key={i} className="bg-stone-800 p-2 rounded border border-stone-600 flex flex-col items-center gap-1 hover:bg-stone-700 transition-colors" title={slot.item.name}>
                                        <div className="w-8 h-8 flex items-center justify-center text-xl bg-stone-900 rounded-full border border-stone-700">
                                            {slot.item.name.includes("Wood") ? "🪵" :
                                                slot.item.name.includes("Stone") ? "🪨" :
                                                    slot.item.name.includes("Food") || slot.item.name.includes("Fruit") ? "🍎" :
                                                        slot.item.name.includes("Wall") ? "🧱" : "📦"
                                            }
                                        </div>
                                        <span className="text-[10px] font-bold text-center leading-tight">{slot.item.name}</span>
                                        <span className="text-xs text-yellow-500 font-mono">x{slot.count}</span>
                                    </div>
                                ))}
                                {agent.inventory.length === 0 && <div className="col-span-4 text-center py-4 text-stone-500 italic">Inventory is empty</div>}
                            </div>
                        </div>

                        <div>
                            <SectionHeader title="Knowledge" />
                            <div className="flex flex-wrap gap-1">
                                {/* Mock knowledge for now, can be populated from backend later */}
                                <span className="px-2 py-1 bg-stone-800 rounded border border-stone-700 text-xs text-blue-300">Basic Survival</span>
                                {agent.attributes.job === 'Builder' && <span className="px-2 py-1 bg-stone-800 rounded border border-stone-700 text-xs text-orange-300">Construction</span>}
                                {agent.attributes.job === 'Shaman' && <span className="px-2 py-1 bg-stone-800 rounded border border-stone-700 text-xs text-purple-300">Mysticism</span>}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
});

// --- UTILS ---

const Badge = ({ label, value, color }) => (
    <span className={`px-2 py-0.5 rounded-sm text-[10px] font-bold uppercase tracking-wider border border-black/20 shadow-sm ${color}`}>
        {label}: {value}
    </span>
);

const StatusBar = ({ label, value, color }) => (
    <div className="flex items-center gap-2 text-xs">
        <span className="w-24 text-stone-400 font-bold uppercase text-[9px] tracking-wider">{label}</span>
        <div className="flex-1 h-3 bg-stone-900 rounded-sm overflow-hidden border border-stone-700/50">
            <div className={`h-full ${color}`} style={{ width: `${Math.min(100, Math.max(0, value * 100))}%` }}></div>
        </div>
    </div>
);

const SectionHeader = ({ title }) => (
    <h3 className="text-yellow-600/80 font-bold uppercase tracking-[0.2em] text-[10px] border-b border-yellow-900/30 pb-1 mb-3">
        {title}
    </h3>
);

const RelationBox = ({ title, id, name, agentMap, onSelect }) => {
    const target = id ? agentMap[id] : null;
    const displayName = target ? target.attributes.name : name;
    return (
        <div className="bg-stone-800/40 p-2 rounded border border-stone-700/50 flex flex-col">
            <span className="text-[9px] text-stone-500 uppercase tracking-wider">{title}</span>
            {target ? (
                <button
                    onClick={() => onSelect(id)}
                    className="font-bold truncate text-yellow-100 hover:text-yellow-400 hover:underline text-left transition-colors"
                >
                    {displayName}
                </button>
            ) : (
                <span className={`font-bold truncate ${displayName ? 'text-stone-400' : 'text-stone-600 italic'}`}>
                    {displayName || "None"}
                </span>
            )}
        </div>
    );
};

const RelationList = ({ title, ids, names, agentMap, onSelect, empty }) => (
    <div className="bg-stone-800/40 p-2 rounded border border-stone-700/50 flex flex-col gap-1 min-h-[60px]">
        <span className="text-[9px] text-stone-500 uppercase tracking-wider mb-1">{title}</span>
        {ids && ids.length > 0 ? (
            ids.map((id, i) => {
                const target = agentMap[id];
                const displayName = target ? target.attributes.name : (names && names[i] ? names[i] : 'Unknown');

                if (target) {
                    return (
                        <button
                            key={i}
                            onClick={() => onSelect(id)}
                            className="text-xs text-stone-300 bg-stone-900/50 px-1.5 py-0.5 rounded truncate hover:bg-stone-700 hover:text-white transition-colors text-left"
                        >
                            {displayName}
                        </button>
                    );
                } else {
                    return (
                        <span key={i} className="text-xs text-stone-500 bg-stone-900/30 px-1.5 py-0.5 rounded truncate">
                            {displayName}
                        </span>
                    );
                }
            })
        ) : (
            <span className="text-xs text-stone-600 organic italic">{empty}</span>
        )}
    </div>
);


const NotificationContainer = ({ notifications }) => (
    <div className="absolute top-24 right-4 z-50 flex flex-col items-end gap-2 pointer-events-none">
        {notifications.map(n => (
            <div key={n.id} className="animate-slide-in pointer-events-auto bg-stone-900/90 border border-yellow-600/50 text-yellow-100 px-4 py-2 rounded shadow-2xl flex items-center gap-3 w-80 backdrop-blur-md">
                <div className="text-xl">{n.icon}</div>
                <div className="flex flex-col">
                    <span className="text-[10px] uppercase text-stone-500 font-bold tracking-wider">{n.header}</span>
                    <span className="text-xs leading-tight">{n.message}</span>
                </div>
            </div>
        ))}
    </div>
);


// --- MAIN DASHBOARD ---

const Dashboard = ({ gameState, onSelectAgent, selectedAgentId, onTogglePause, mapMode, setMapMode }) => {

    // Notifications State
    const [notifications, setNotifications] = useState([]);
    const lastLogCountRef = useRef(0);

    // Process Logs for Notifications
    useEffect(() => {
        if (!gameState || !gameState.logs) return;

        const logs = gameState.logs; // Array of strings "[Step X] Msg"
        if (logs.length > lastLogCountRef.current) {
            // New logs appeared
            const newLogs = logs.slice(lastLogCountRef.current);

            const newNotifs = newLogs.map((log, i) => {
                // Parse rudimentary content detection
                let icon = "📜";
                let header = "Event";
                if (log.toLowerCase().includes("born")) { icon = "👶"; header = "Birth"; }
                else if (log.toLowerCase().includes("died")) { icon = "💀"; header = "Death"; }
                else if (log.toLowerCase().includes("founded")) { icon = "🚩"; header = "Tribe Founded"; }
                else if (log.toLowerCase().includes("joined")) { icon = "🤝"; header = "Alliance"; }
                else if (log.toLowerCase().includes("traded") || log.toLowerCase().includes("gifted")) { icon = "⚖️"; header = "Trade"; }

                return {
                    id: Date.now() + i,
                    message: log.replace(/\[Step \d+\] /, ''),
                    icon,
                    header
                };
            });

            setNotifications(prev => [...newNotifs, ...prev].slice(0, 5)); // Keep last 5

            // Auto dismiss
            setTimeout(() => {
                setNotifications(prev => prev.filter(n => !newNotifs.find(nn => nn.id === n.id)));
            }, 5000);
        }
        lastLogCountRef.current = logs.length;
    }, [gameState?.logs]); // Only run when logs change

    const selectedAgent = useMemo(() =>
        gameState && gameState.agents ? gameState.agents.find(a => a.id === selectedAgentId) : null,
        [gameState, selectedAgentId]);

    // Memoize agent lookup map for O(1) access
    const agentMap = useMemo(() => {
        if (!gameState || !gameState.agents) return {};
        return gameState.agents.reduce((acc, agent) => {
            acc[agent.id] = agent;
            return acc;
        }, {});
    }, [gameState?.agents]);

    if (!gameState) return <div className="absolute top-0 left-0 text-yellow-500 font-serif p-4">Loading World State...</div>;

    return (
        <div className="absolute inset-0 pointer-events-none w-full h-full overflow-hidden font-sans selection:bg-yellow-900 selection:text-white">
            <TopBar gameState={gameState} onTogglePause={onTogglePause} />
            <NotificationContainer notifications={notifications} />
            <AgentList agents={gameState.agents} selectedAgentId={selectedAgentId} onSelectAgent={onSelectAgent} />
            <MapModeSelector mapMode={mapMode} setMapMode={setMapMode} />
            <CharacterSheet agent={selectedAgent} gameState={gameState} onSelectAgent={onSelectAgent} agentMap={agentMap} />
        </div>
    );
};

export default Dashboard;
