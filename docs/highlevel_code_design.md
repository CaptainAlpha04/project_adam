# High-Level Code Design: Project Adam

This document provides a detailed overview of the **Project Adam** codebase, explaining the architecture, the role of each file, and how data flows through the system.

## 1. System Architecture

Project Adam follows a classic Client-Server architecture:

-   **Backend:** A Python-based `FastAPI` server that acts as the simulation engine. It runs the game loop, processes interactions (Agents, Animals, Physics), and manages the persistent state. It supports both a "Play Mode" (WebSocket stream) and a "Training Mode" (Reinforcement Learning using Stable Baselines 3).
-   **Frontend:** A React application (runs via Vite) that visualizes the simulation. It receives the state updates 60 times a second (or less depending on speed) and renders the world on an HTML5 Canvas, overlaying a rich HUD for inspection.

---

## 2. Backend Structure (`backend/app/`)

The backend logic is distributed across modular directories.

### Root Files

-   **`main.py`**: The entry point of the server.
    -   Initializes `FastAPI` and `Socket.IO`.
    -   **Simulation Loop**: A `while True` loop inside the websocket endpoint that advances `world` steps, handles simulation speed, and broadcasts state to the frontend.
    -   **Integration**: Mounts routers and handles `WebSocket` connections for the main game view.
-   **`debug_ws.py`**: A simple standalone script for testing WebSocket connectivity without the full frontend.
-   **`run_test_world.py`**: CLI script to run the world simulation in a headless mode for verification or performance testing.

### Core Environment (`env/`)

-   **`world.py`**: The "God Class" containing the entire simulation state.
    -   **Grid Management**: Stores the `terrain_grid` (Numpy array) and `items_grid` (Spatial Hash).
    -   **Entity Registry**: Maintains lists of all `Agent` and `Animal` instances.
    -   **Terrain Generation**: Uses `_generate_terrain` with Perlin Noise to create biomes (Forest, Desert, Mountain).
    -   **Time**: Tracks global `time_step` and handles `respawn_resources`.
-   **`animals.py`**: Defines the `Animal` class (Herbivores/Carnivores).
    -   **AI**: Implements Finite State Machine (FSM) logic for `Flee`, `Graze`, and `Hunt`.
    -   **Herding**: Contains logic for flocking behaviors (Cohesion).
-   **`item.py`**: Data definition for objects in the world.
    -   **`Item` Class**: Properties like `weight`, `hardness`, `tags`.
    -   **`RECIPES`**: A dictionary defining crafting recipes (e.g., Wood + Stone = Hammer).
-   **`tile.py`**: (Deprecated/Minimal) Simple data structure for tile properties if needed.
-   **`gym_env.py`**: Custom Gymnasium wrappers to adapt the `World` for RL training (Observation Space / Action Space definition).

### Agent Logic (`agents/`)

-   **`agent.py`**: The core implementation of the intelligent entities.
    -   **`Agent` Class**: Main controller.
    -   **Psyche Architecture**:
        -   **`Nafs`**: Biological survival layer (Hunger, Health, Pain). Overrides control for survival.
        -   **`Qalb`**: Emotional/Social layer. Maintains `opinions`, calculates `happiness`, and determines "Desires" (Socialize, Trade, etc.).
        -   **`Ruh`**: Spiritual layer. Tracks `Karma`, `Life Goals` (e.g., "Sage"), and acts as a high-level moral filter.
    -   **`act()`**: The main decision loop called every tick.
-   **`brain.py`**: The Planning unit.
    -   **`AgentBrain`**: Manages the Action Queue.
    -   **Planning**: Generates sequences of actions (e.g., `find_resource` -> `eat`) to fulfill high-level goals set by `Qalb`.
    -   **Sticky Actions**: Handles long-running tasks that span multiple ticks.

### Social Logic (`social/`)

-   **`tribe.py`**: Groups agents into factions.
    -   **`Tribe` Class**: Manages leadership (`leader_id`), `members`, and collective resources.
    -   **Logic**: Calculates `harmony` (average opinion of members) and sets collective `goals` (e.g., "Declare War", "Gather Food").

### Simulation & RL (`rl/` & `api/`)

-   **`api/training.py`**: API endpoints (`/start`, `/stop`) to control background training sessions from the GUI.
-   **`rl/training_manager.py`**: A Singleton manager that runs Stable Baselines 3 training in a separate thread. It bridges the sync training loop with the async WebSocket emitter.
-   **`rl/callbacks.py`**: Custom SB3 callbacks to stream training metrics (Reward, Loss, Map Preview) to the frontend in real-time.
-   **`rl/envs.py`**: Specific Gym Environments for different training scenarios (Movement, Crafting, Social).

---

## 3. Frontend Structure (`frontend/src/`)

The frontend is a React Single Page Application (SPA).

### Components (`components/`)

-   **`MapCanvas.jsx`**: The core visualization component.
    -   **Technology**: Uses HTML5 Canvas API (`2d` context) for performance (rendering thousands of tiles/entities).
    -   **Features**: Handles Camera (Pan/Zoom), Rendering Layers (Terrain -> Items -> Agents -> Overlays -> Fog of War/Night).
-   **`Dashboard.jsx`**: The Game HUD (Heads-Up Display).
    -   **UI**: Renders the top bar (Global Stats), Agent List, and the detailed "Character Sheet" popup.
    -   **Logic**: Parses game logs to generate notifications (Births, Deaths, Trades).
-   **`Training/`**:
    -   **`TrainingCenter.jsx`**: The UI for the "Matrix Mode" (Training View). Allows users to start/stop training runs and configure scenarios.
    -   **`TrainingVisualizer.jsx`**: A specialized, lightweight map renderer to show the *training* environment (often faster/simpler than the main game map) in real-time via Socket.IO events.

### Main Logic

-   **`App.jsx`**: The root component.
    -   **State**: Holds the global `gameState`.
    -   **Networking**: Manages the primary WebSocket connection to `main.py`.
    -   **Routing**: Switches between the "Simulation View" (`Dashboard` + `MapCanvas`) and "Training View".

---

## 4. Key Data Flows

### 1. The Game Loop (Main Simulation)
1.  **Backend (`main.py`)**: Timer triggers. Calls `world.act()` -> `agent.act()`.
2.  **State Update**: Agent logic updates positions, inventories, and opinions.
3.  **Serialization**: `world.get_state()` converts objects to a optimized JSON-safe dict.
4.  **Broadcast**: `websocket.send_json(state)` pushes data to frontend.
5.  **Frontend (`App.jsx`)**: Updates `gameState`.
6.  **Render (`MapCanvas.jsx`)**: Draws the new frame.

### 2. The Training Loop (RL)
1.  **Frontend (`TrainingCenter`)**: User clicks "Start Training". POST `/train/start`.
2.  **Backend (`training_manager.py`)**: Spawns a new thread.
3.  **RL Engine**: SB3 `model.learn()` runs thousands of fast steps on `gym_env.py` (headless).
4.  **Feedback**: `SocketCallback` captures a frame every ~0.5s and emits it via Socket.IO.
5.  **Visualization**: `TrainingVisualizer.jsx` renders this preview so the user sees the AI learning.

### 3. Agent Decision Flow
1.  **Input**: Agent perceives surroundings (`scan_surroundings`).
2.  **Psyche**: 
    -   `Nafs` updates hunger.
    -   `Qalb` updates loneliness. 
    -   `Brain` checks current plan validity.
3.  **Proposal**: `Qalb` suggests "Socialize".
4.  **Veto**: `Ruh` checks Karma. If valid, approves.
5.  **Action**: `Brain` queues "Go to Agent X" -> "Interact".
6.  **Execution**: `agent.move_by(...)` changes `x,y`.
