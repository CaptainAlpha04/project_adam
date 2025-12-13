import React, { useEffect, useRef } from 'react';

const TrainingVisualizer = ({ mapData }) => {
    const canvasRef = useRef(null);

    useEffect(() => {
        if (!mapData || !canvasRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const { width, height, agent, food, items, others } = mapData;

        // Scale
        const cellSize = Math.min(canvas.width / width, canvas.height / height);

        // Clear
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw Grid (Optional, faint)
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 0.5;
        for (let i = 0; i <= width; i++) {
            ctx.beginPath(); ctx.moveTo(i * cellSize, 0); ctx.lineTo(i * cellSize, height * cellSize); ctx.stroke();
        }
        for (let i = 0; i <= height; i++) {
            ctx.beginPath(); ctx.moveTo(0, i * cellSize); ctx.lineTo(width * cellSize, i * cellSize); ctx.stroke();
        }

        // Draw Food
        ctx.fillStyle = '#4ade80'; // Green
        if (food) {
            food.forEach(f => {
                ctx.beginPath();
                ctx.arc(f.x * cellSize + cellSize / 2, f.y * cellSize + cellSize / 2, cellSize / 3, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // Draw Items
        if (items) {
            items.forEach(item => {
                ctx.fillStyle = item.type === 'tree' ? '#166534' : '#57534e'; // Dark Green or Stone Gray
                ctx.beginPath();
                if (item.type === 'tree') {
                    ctx.moveTo(item.x * cellSize + cellSize / 2, item.y * cellSize);
                    ctx.lineTo(item.x * cellSize + cellSize, item.y * cellSize + cellSize);
                    ctx.lineTo(item.x * cellSize, item.y * cellSize + cellSize);
                } else {
                    ctx.rect(item.x * cellSize + cellSize / 4, item.y * cellSize + cellSize / 4, cellSize / 2, cellSize / 2);
                }
                ctx.fill();
            });
        }

        // Draw Other Agents
        if (others) {
            ctx.fillStyle = '#ef4444'; // Red
            others.forEach(other => {
                ctx.beginPath();
                ctx.arc(other.x * cellSize + cellSize / 2, other.y * cellSize + cellSize / 2, cellSize / 2.5, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // Draw Agent
        if (agent) {
            ctx.fillStyle = '#60a5fa'; // Blue
            ctx.beginPath();
            ctx.arc(agent.x * cellSize + cellSize / 2, agent.y * cellSize + cellSize / 2, cellSize / 2.5, 0, Math.PI * 2);
            ctx.fill();

            // Eye/Direction (Optional)
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(agent.x * cellSize + cellSize / 2, agent.y * cellSize + cellSize / 2, cellSize / 6, 0, Math.PI * 2);
            ctx.fill();
            // Draw Opinions (Inter-agent relationships)
            // Agent is "Me", others are potential patterns
            // Draw Opinions & Interactions
            if (agent && others) {
                // Map ID to Agent for lookup
                const agentMap = new Map();
                others.forEach(o => agentMap.set(o.id, o));

                // 1. Opinions (Lines)
                if (agent.opinions) {
                    others.forEach(other => {
                        const opinion = agent.opinions[other.id] || 0;
                        if (Math.abs(opinion) > 0.1) {
                            ctx.beginPath();
                            ctx.moveTo(agent.x * cellSize + cellSize / 2, agent.y * cellSize + cellSize / 2);
                            ctx.lineTo(other.x * cellSize + cellSize / 2, other.y * cellSize + cellSize / 2);
                            // Green for like, Red for dislike
                            ctx.strokeStyle = opinion > 0 ? `rgba(74, 222, 128, ${Math.min(Math.abs(opinion), 1)})` : `rgba(239, 68, 68, ${Math.min(Math.abs(opinion), 1)})`;
                            ctx.lineWidth = Math.max(1, Math.abs(opinion) * 2);
                            ctx.stroke();
                        }
                    });
                }

                // 2. Last Interaction (Events)
                if (agent.state && agent.state.last_interaction) {
                    const li = agent.state.last_interaction;
                    const partner = agentMap.get(li.partner);

                    if (partner) {
                        ctx.beginPath();
                        ctx.moveTo(agent.x * cellSize + cellSize / 2, agent.y * cellSize + cellSize / 2);
                        ctx.lineTo(partner.x * cellSize + cellSize / 2, partner.y * cellSize + cellSize / 2);

                        let showIcon = "";

                        if (li.type === 'love') {
                            ctx.strokeStyle = '#ec4899'; // Pink
                            ctx.lineWidth = 4;
                            showIcon = "♥";
                        } else if (li.type === 'reproduce') {
                            ctx.strokeStyle = '#eab308'; // Gold
                            ctx.lineWidth = 5;
                            showIcon = "★";
                        } else if (li.type === 'combat') {
                            ctx.strokeStyle = '#991b1b'; // Dark Red
                            ctx.lineWidth = 4;
                            showIcon = "⚔️";
                        } else if (li.type === 'conflict') {
                            ctx.strokeStyle = '#f87171'; // Light Red
                            ctx.lineWidth = 2;
                        } else {
                            // Chat
                            ctx.strokeStyle = '#ffffff';
                            ctx.lineWidth = 1;
                        }

                        ctx.stroke();

                        if (showIcon) {
                            ctx.font = "20px Arial";
                            ctx.fillStyle = ctx.strokeStyle;
                            ctx.textAlign = "center";
                            ctx.textBaseline = "middle";
                            ctx.fillText(showIcon, (agent.x + partner.x) / 2 * cellSize + cellSize / 2, (agent.y + partner.y) / 2 * cellSize);
                        }
                    }
                }
            }
        }

    }, [mapData]);

    return (
        <div className="bg-black rounded-lg overflow-hidden border border-gray-700 shadow-lg">
            <canvas
                ref={canvasRef}
                width={400}
                height={400}
                className="w-full h-full object-contain"
            />
        </div>
    );
};

export default TrainingVisualizer;
