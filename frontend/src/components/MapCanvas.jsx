import React, { useRef, useEffect, useState } from 'react';

const MapCanvas = ({ gameState, selectedAgentId, onSelectAgent }) => {
  const canvasRef = useRef(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [scale, setScale] = useState(1);
  const [isDragging, setIsDragging] = useState(false);
  const [lastPos, setLastPos] = useState({ x: 0, y: 0 });
  const [dragStartPos, setDragStartPos] = useState({ x: 0, y: 0 });

  const TILE_SIZE = 10;

  // Zoom to selected agent when selection changes
  useEffect(() => {
    if (selectedAgentId && gameState && gameState.agents) {
      const agent = gameState.agents.find(a => a.id === selectedAgentId);
      if (agent && canvasRef.current) {
        const canvas = canvasRef.current;
        const newScale = 3.0; // Zoom in
        const newOffsetX = canvas.width / 2 - (agent.x * TILE_SIZE + TILE_SIZE / 2) * newScale;
        const newOffsetY = canvas.height / 2 - (agent.y * TILE_SIZE + TILE_SIZE / 2) * newScale;
        setScale(newScale);
        setOffset({ x: newOffsetX, y: newOffsetY });
      }
    }
  }, [selectedAgentId]); // Only run when selection changes

  // Terrain Colors
  const TERRAIN_COLORS = {
    0: '#3b82f6', // Water
    1: '#fde047', // Sand
    2: '#22c55e', // Grass
    3: '#15803d', // Forest
    4: '#78716c', // Mountain
    5: '#f8fafc', // Snow
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Clear canvas
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    if (!gameState) return;

    ctx.save();
    // Apply transformations
    ctx.translate(offset.x, offset.y);
    ctx.scale(scale, scale);

    // 1. Draw Terrain
    if (gameState.terrain) {
      gameState.terrain.forEach((row, y) => {
        row.forEach((tileType, x) => {
          ctx.fillStyle = TERRAIN_COLORS[tileType] || '#000';
          ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);

          // Draw Trees on Forest
          if (tileType === 3) {
            ctx.fillStyle = '#052e16';
            ctx.beginPath();
            ctx.arc(x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2, TILE_SIZE / 4, 0, Math.PI * 2);
            ctx.fill();
          }
        });
      });
    }

    // 2. Draw Items
    if (gameState.items) {
      gameState.items.forEach(item => {
        if (item.tags && item.tags.includes('red')) {
          ctx.fillStyle = '#ef4444'; // Red Fruit
        } else {
          ctx.fillStyle = '#a8a29e'; // Stone/Item color
        }
        ctx.beginPath();
        ctx.arc(item.x * TILE_SIZE + TILE_SIZE / 2, item.y * TILE_SIZE + TILE_SIZE / 2, TILE_SIZE / 4, 0, 2 * Math.PI);
        ctx.fill();
      });
    }

    // 3. Draw Animals
    if (gameState.animals) {
      gameState.animals.forEach(animal => {
        ctx.fillStyle = animal.type === 'carnivore' ? '#000000' : '#fbbf24'; // Black or Yellow
        ctx.beginPath();
        ctx.arc(animal.x * TILE_SIZE + TILE_SIZE / 2, animal.y * TILE_SIZE + TILE_SIZE / 2, TILE_SIZE / 2 - 1, 0, 2 * Math.PI);
        ctx.fill();
      });
    }

    // 3.5. Draw Opinions (Social Network Overlay)
    if (gameState.agents) {
      // Map ID to agent for lines
      const agentMap = new Map();
      gameState.agents.forEach(a => agentMap.set(a.id, a));

      gameState.agents.forEach(agent => {
        if (!agent.opinions) return;

        Object.entries(agent.opinions).forEach(([targetId, score]) => {
          if (Math.abs(score) < 0.1) return; // Ignore weak opinions

          const target = agentMap.get(targetId);
          if (target) {
            ctx.beginPath();
            ctx.moveTo(agent.x * TILE_SIZE + TILE_SIZE / 2, agent.y * TILE_SIZE + TILE_SIZE / 2);
            ctx.lineTo(target.x * TILE_SIZE + TILE_SIZE / 2, target.y * TILE_SIZE + TILE_SIZE / 2);

            // Color: Green (Like) / Red (Dislike)
            ctx.strokeStyle = score > 0
              ? `rgba(74, 222, 128, ${Math.min(Math.abs(score), 0.8)})`
              : `rgba(239, 68, 68, ${Math.min(Math.abs(score), 0.8)})`;

            ctx.lineWidth = Math.max(0.5, Math.abs(score) * 1.5);
            ctx.stroke();
          }
        });

        // Visualize Interactions (Hearts/Swords)
        if (agent.state && agent.state.last_interaction) {
          const li = agent.state.last_interaction;
          // Only show recent interaction (e.g. within last 10 ticks) - Backend needs to clear it or we just show it? 
          // The timestamp check is needed if we want it to fade. For now showing static.
          const partner = agentMap.get(li.partner);
          if (partner && (li.type === 'love' || li.type === 'combat' || li.type === 'reproduce')) {
            const mx = (agent.x + partner.x) / 2 * TILE_SIZE + TILE_SIZE / 2;
            const my = (agent.y + partner.y) / 2 * TILE_SIZE + TILE_SIZE / 2;

            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            if (li.type === 'love') ctx.fillText('♥', mx, my);
            else if (li.type === 'reproduce') ctx.fillText('★', mx, my);
            else if (li.type === 'combat') ctx.fillText('⚔️', mx, my);
          }
        }
      });
    }

    // 4. Draw Agents
    if (gameState.agents) {
      gameState.agents.forEach(agent => {
        ctx.fillStyle = agent.attributes.gender === 'male' ? '#3b82f6' : '#ec4899'; // Blue or Pink
        ctx.beginPath();
        ctx.arc(agent.x * TILE_SIZE + TILE_SIZE / 2, agent.y * TILE_SIZE + TILE_SIZE / 2, TILE_SIZE / 2 - 1, 0, 2 * Math.PI);
        ctx.fill();

        // Selection Highlight
        if (selectedAgentId === agent.id) {
          ctx.strokeStyle = '#fff';
          ctx.lineWidth = 2;
          ctx.stroke();
        }

        // Agent Name (only if zoomed in enough)
        if (scale > 0.5) {
          ctx.fillStyle = '#fff';
          ctx.font = '3px Arial';
          ctx.textAlign = 'center';
          ctx.fillText(agent.attributes.name, agent.x * TILE_SIZE + TILE_SIZE / 2, agent.y * TILE_SIZE - 2);
        }
      });
    }

    ctx.restore();
  }, [gameState, offset, scale, selectedAgentId]);

  const handleWheel = (e) => {
    e.preventDefault();
    const zoomSensitivity = 0.001;
    const newScale = Math.min(Math.max(0.1, scale - e.deltaY * zoomSensitivity), 5);
    setScale(newScale);
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setLastPos({ x: e.clientX, y: e.clientY });
    setDragStartPos({ x: e.clientX, y: e.clientY });
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

    // Check if it was a click (minimal movement)
    const dist = Math.sqrt(Math.pow(e.clientX - dragStartPos.x, 2) + Math.pow(e.clientY - dragStartPos.y, 2));

    if (dist < 5) {
      handleCanvasClick(e);
    }
  };

  const handleCanvasClick = (e) => {
    if (!gameState || !gameState.agents) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Convert screen coords to world coords
    const worldX = (mouseX - offset.x) / scale / TILE_SIZE;
    const worldY = (mouseY - offset.y) / scale / TILE_SIZE;

    // Find clicked agent
    const clickedAgent = gameState.agents.find(agent => {
      const dx = agent.x - worldX;
      const dy = agent.y - worldY;
      return Math.sqrt(dx * dx + dy * dy) < 1.5; // Click radius tolerance
    });

    if (clickedAgent) {
      onSelectAgent(clickedAgent.id);
    } else {
      onSelectAgent(null);
    }
  };

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={600}
      className="w-full h-full block"
      style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={() => setIsDragging(false)}
    />
  );
};

export default MapCanvas;
