import React, { useRef, useEffect, useState } from 'react';

const MapCanvas = ({ gameState, selectedAgentId, onSelectAgent, mapMode = 'TERRAIN' }) => {
  const canvasRef = useRef(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [scale, setScale] = useState(1.5); // Start slightly zoomed in
  const [isDragging, setIsDragging] = useState(false);
  const [lastPos, setLastPos] = useState({ x: 0, y: 0 });
  const [dragStartPos, setDragStartPos] = useState({ x: 0, y: 0 });

  const TILE_SIZE = 12; // Slightly larger base tile

  // Zoom to selected agent when selection changes
  useEffect(() => {
    if (selectedAgentId && gameState && gameState.agents) {
      const agent = gameState.agents.find(a => a.id === selectedAgentId);
      if (agent && canvasRef.current) {
        const canvas = canvasRef.current;
        // Smoothly target the agent
        const targetScale = 3.5;
        const targetX = canvas.width / 2 - (agent.x * TILE_SIZE + TILE_SIZE / 2) * targetScale;
        const targetY = canvas.height / 2 - (agent.y * TILE_SIZE + TILE_SIZE / 2) * targetScale;

        setScale(targetScale);
        setOffset({ x: targetX, y: targetY });
      }
    }
  }, [selectedAgentId]);

  // Terrain & Map Colors
  const COLORS = {
    WATER: '#1e3a8a', // Deep Blue
    SAND: '#d4b483', // Muted Gold/Sand
    GRASS: '#3f6212', // Deep Olive Green (CK3 style)
    FOREST: '#14532d', // Dark Pine
    MOUNTAIN: '#57534e', // Stone Grey
    SNOW: '#e2e8f0', // Dull White
    GRID: 'rgba(0, 0, 0, 0.15)', // Subtle grid
    BG: '#0f172a', // Canvas bg
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { alpha: false }); // Optimize

    // Resizing canvas to match display size for sharpness
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    // Initial Fill
    ctx.fillStyle = COLORS.BG;
    ctx.fillRect(0, 0, rect.width, rect.height);

    if (!gameState) return;

    ctx.save();
    // Apply View Transform
    ctx.translate(offset.x, offset.y);
    ctx.scale(scale, scale);

    // --- DRAWING LAYERS ---

    // 1. TERRAIN & DECOR
    if (gameState.terrain) {
      gameState.terrain.forEach((row, y) => {
        row.forEach((tileType, x) => {
          let color = '#000';
          switch (tileType) {
            case 0: color = COLORS.WATER; break;
            case 1: color = COLORS.SAND; break;
            case 2: color = COLORS.GRASS; break;
            case 3: color = '#14532d'; break; // Dark Green Block for Trees
            case 4: color = COLORS.MOUNTAIN; break;
            case 5: color = COLORS.SNOW; break;
            default: color = '#000';
          }

          ctx.fillStyle = color;
          ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);

          // Grid Lines (Only visible at high zoom)
          if (scale > 2) {
            ctx.strokeStyle = COLORS.GRID;
            ctx.lineWidth = 0.5 / scale;
            ctx.strokeRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
          }


        });
      });
    }

    // 2. ITEMS
    if (gameState.items) {
      gameState.items.forEach(item => {
        let color = '#d4d4d4'; // Default grey
        let shape = 'circle';

        if (item) {
          const t = item.tags || [];
          const n = (item.name || "").toLowerCase();
          const id = (item.id || "").toLowerCase();

          // Check ID first as user requested, then Name, then Tags
          if (id.includes('fruit') || n.includes('fruit') || t.includes('food')) { color = '#ef4444'; shape = 'circle'; } // Red Food
          else if (id.includes('wood') || n.includes('wood') || t.includes('wood')) { color = '#ae6033ff'; shape = 'circle'; } // Brown Wood
          else if (id.includes('stone') || n.includes('stone') || t.includes('stone')) { color = '#57534e'; shape = 'rect'; } // Grey Stone
          else if (t.includes('tool') || t.includes('weapon')) { color = '#eab308'; shape = 'triangle'; } // Gold Tool
        }

        ctx.fillStyle = color;
        const cx = (item.x + 0.5) * TILE_SIZE;
        const cy = (item.y + 0.5) * TILE_SIZE;
        const s = TILE_SIZE * 0.4;

        ctx.beginPath();
        if (shape === 'circle') {
          ctx.arc(cx, cy, s / 2, 0, Math.PI * 2);
        } else if (shape === 'rect') {
          ctx.fillRect(cx - s / 2, cy - s / 2, s, s);
        } else {
          // Triangle for tools
          ctx.moveTo(cx, cy - s / 2);
          ctx.lineTo(cx + s / 2, cy + s / 2);
          ctx.lineTo(cx - s / 2, cy + s / 2);
          ctx.closePath();
        }
        ctx.fill();

        ctx.strokeStyle = 'black';
        ctx.lineWidth = 1 / scale;
        ctx.stroke(); // Add outline
      });
    }

    // 3. AGENTS
    if (gameState.agents) {
      gameState.agents.forEach(agent => {
        const cx = (agent.x + 0.5) * TILE_SIZE;
        const cy = (agent.y + 0.5) * TILE_SIZE;
        const radius = TILE_SIZE * 0.4;

        // Base Color
        let color = agent.attributes.gender === 'male' ? '#3b82f6' : '#ec4899';
        if (mapMode === 'POLITICAL' && agent.attributes.tribe_color) {
          color = agent.attributes.tribe_color;
        }

        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();

        // Stroke (Gold for Leader, White for selected, Black for normal)
        ctx.lineWidth = 2 / scale;
        if (selectedAgentId === agent.id) {
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 4 / scale;
        } else if (agent.attributes.leader_id === agent.id) {
          ctx.strokeStyle = '#fbbf24'; // Gold
        } else {
          ctx.strokeStyle = 'rgba(0,0,0,0.6)';
        }
        ctx.stroke();

        // Direction / Face
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(cx, cy - radius * 0.3, radius * 0.2, 0, Math.PI * 2);
        ctx.fill();

        // Name Tag (Zoom dependent)
        if (scale > 2.5) {
          ctx.fillStyle = 'white';
          ctx.font = `bold ${Math.max(10, 4 / scale)}px sans-serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'bottom';
          ctx.shadowColor = 'black';
          ctx.shadowBlur = 4;
          ctx.lineWidth = 3;
          ctx.fillText(agent.attributes.name, cx, cy - radius * 1.5);
          ctx.shadowBlur = 0;
        }
      });
    }

    // 4. ANIMALS
    if (gameState.animals) {
      gameState.animals.forEach(anim => {
        const cx = (anim.x + 0.5) * TILE_SIZE;
        const cy = (anim.y + 0.5) * TILE_SIZE;

        let color = '#a8a29e'; // Default Grey
        if (anim.type === 'carnivore') color = '#000000'; // Black Triangle for Predators
        else if (anim.type === 'herbivore') color = '#f97316'; // Orange Triangle for Herbivores

        ctx.fillStyle = color;
        ctx.beginPath();
        // Triangle shape for animals to distinguish from agents (circles)
        const s = TILE_SIZE * 0.5;
        ctx.moveTo(cx, cy - s / 2);
        ctx.lineTo(cx + s / 2, cy + s / 2);
        ctx.lineTo(cx - s / 2, cy + s / 2);
        ctx.closePath();
        ctx.fill();

        // Eye
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(cx, cy - s / 6, s / 10, 0, Math.PI * 2);
        ctx.fill();
      });
    }

    // 5. CONNECTIONS (Selected Agent)
    const selectedAgent = gameState.agents.find(a => a.id === selectedAgentId);
    if (selectedAgent && selectedAgent.qalb && selectedAgent.qalb.opinions) {
      const agentMap = new Map(gameState.agents.map(a => [a.id, a]));
      const sx = (selectedAgent.x + 0.5) * TILE_SIZE;
      const sy = (selectedAgent.y + 0.5) * TILE_SIZE;

      Object.entries(selectedAgent.qalb.opinions).forEach(([tid, val]) => {
        const target = agentMap.get(tid);
        if (target && Math.abs(val) > 5) { // Only strong opinions
          ctx.beginPath();
          ctx.moveTo(sx, sy);
          ctx.lineTo((target.x + 0.5) * TILE_SIZE, (target.y + 0.5) * TILE_SIZE);
          ctx.strokeStyle = val > 0 ? `rgba(34, 197, 94, ${Math.min(1, val / 50)})` : `rgba(239, 68, 68, ${Math.min(1, Math.abs(val) / 50)})`;
          ctx.lineWidth = 2 / scale;
          ctx.setLineDash([5 / scale, 5 / scale]);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      });
    }

    // 6. NIGHT OVERLAY
    if (!gameState.is_day) {
      ctx.fillStyle = 'rgba(15, 23, 42, 0.4)'; // Slate 900, 40%
      // ctx.fillRect(-1000, -1000, 10000, 10000); // Hacky cover
      // Better:
      // Reset transform to draw fullscreen overlay?
      // Actually, just drawing it over the probable map area is enough
      // but to be safe let's pop logic
    }

    ctx.restore();

    // UI Overlay on Canvas (Screen Space)
    if (!gameState.is_day) {
      ctx.fillStyle = 'rgba(15, 23, 42, 0.6)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.font = 'bold 24px serif';
      ctx.fillStyle = '#94a3b8';
      ctx.textAlign = 'right';
      ctx.fillText("NIGHT", canvas.width - 20, 40);
    }


  }, [gameState, offset, scale, selectedAgentId, mapMode]);

  // --- CONTROLS ---

  const handleWheel = (e) => {
    e.preventDefault();
    const zoomSensitivity = 0.001;
    const delta = -e.deltaY; // deltaY is positive for scrolling down (zoom out)
    const newScale = Math.min(Math.max(0.5, scale + delta * zoomSensitivity * scale), 10);

    // Zoom towards mouse pointer
    const rect = canvasRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // derived from: (world - offset) / oldScale = (world - newOffset) / newScale
    const worldX = (mouseX - offset.x) / scale;
    const worldY = (mouseY - offset.y) / scale;

    const newOffsetX = mouseX - worldX * newScale;
    const newOffsetY = mouseY - worldY * newScale;

    setScale(newScale);
    setOffset({ x: newOffsetX, y: newOffsetY });
  };

  const handleMouseDown = (e) => {
    if (e.button === 0 || e.button === 1) { // Left or Middle click
      setIsDragging(true);
      setLastPos({ x: e.clientX, y: e.clientY });
      setDragStartPos({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      const dx = e.clientX - lastPos.x;
      const dy = e.clientY - lastPos.y;
      setOffset(prev => ({ x: prev.x + dx, y: prev.y + dy }));
      setLastPos({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseUp = (e) => {
    setIsDragging(false);
    const dist = Math.sqrt(Math.pow(e.clientX - dragStartPos.x, 2) + Math.pow(e.clientY - dragStartPos.y, 2));
    if (dist < 5) handleCanvasClick(e);
  };

  const handleCanvasClick = (e) => {
    if (!gameState || !gameState.agents) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const worldX = (mouseX - offset.x) / scale / TILE_SIZE;
    const worldY = (mouseY - offset.y) / scale / TILE_SIZE;

    // Find clicked
    const clickedAgent = gameState.agents.find(agent => {
      const dx = agent.x + 0.5 - worldX; // Center offset correction
      const dy = agent.y + 0.5 - worldY;
      return Math.sqrt(dx * dx + dy * dy) < 0.8;
    });

    if (clickedAgent) {
      onSelectAgent(clickedAgent.id);
    } else {
      onSelectAgent(null);
    }
  };

  return (
    <div className="w-full h-full bg-slate-900 border-4 border-yellow-900/30 overflow-hidden relative shadow-inner">
      <canvas
        ref={canvasRef}
        className="w-full h-full block touch-none"
        style={{ width: '100%', height: '100%', cursor: isDragging ? 'grabbing' : 'grab' }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={() => setIsDragging(false)}
        onContextMenu={(e) => e.preventDefault()}
      />
      {/* Mini Controls overlay */}
      <div className="absolute bottom-4 right-4 flex gap-2">
        <button onClick={() => setScale(s => s * 1.2)} className="w-8 h-8 bg-zinc-800 text-yellow-500 border border-yellow-700 rounded hover:bg-zinc-700 font-bold">+</button>
        <button onClick={() => setScale(s => s / 1.2)} className="w-8 h-8 bg-zinc-800 text-yellow-500 border border-yellow-700 rounded hover:bg-zinc-700 font-bold">-</button>
      </div>
    </div>
  );
};

export default MapCanvas;
