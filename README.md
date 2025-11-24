# Project Adam

Project Adam is a complex multi-agent simulation designed to explore emergent behavior, survival dynamics, and social interactions in a procedurally generated world.

## 🌍 Overview

The simulation features autonomous agents that navigate a dynamic environment, manage their survival needs (hunger, thirst, happiness), and interact with the world and each other. The project aims to simulate the evolution of a small society from basic survival to complex social structures.

### Key Features

-   **Autonomous Agents**:
    -   **Personality System**: Agents possess unique personalities based on the Big 5 traits (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism), influencing their behavior and "Traits" (e.g., Curious, Lazy, Social).
    -   **Survival Logic**: Agents must eat, drink, and sleep to survive. They can hunt animals, gather fruits, and chop wood.
    -   **Memory & Goals**: Agents have short-term (e.g., "Find Food", "Flee Predator") and long-term goals ("Thrive"), along with a memory log of significant events.
    -   **Lifecycle**: Agents can reproduce, passing on traits to their offspring, and can die from starvation or predation.

-   **Dynamic Environment**:
    -   **Procedural Generation**: The world is generated using Perlin noise, creating diverse biomes (Forest, Grassland, Mountain, Water).
    -   **Ecosystem**: The world is populated with resources (Trees, Rocks, Fruits) and animals (Herbivores, Carnivores) that interact with the agents.
    -   **Persistent Map**: The map generation uses a fixed seed for consistency across runs.

-   **Interactive Dashboard**:
    -   **Real-time Visualization**: A React-based frontend renders the simulation in real-time using HTML5 Canvas.
    -   **CK3-Style Inspector**: Click on any agent to view a detailed, Crusader Kings 3-inspired character pane showing their stats, inventory, traits, goals, and full diary history.
    -   **Simulation Control**: Pause and resume the simulation at will.

## 🛠️ Tech Stack

-   **Backend**:
    -   **Python**: Core simulation logic.
    -   **FastAPI**: Web server and WebSocket management.
    -   **NumPy**: Efficient grid and vector calculations.
    -   **Uvicorn**: ASGI server.

-   **Frontend**:
    -   **React**: UI framework.
    -   **Tailwind CSS**: Styling.
    -   **WebSocket**: Real-time state synchronization.

## 🚀 Getting Started

### Prerequisites

-   Python 3.8+
-   Node.js 14+

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/project-adam.git
    cd project-adam
    ```

2.  **Backend Setup**:
    ```bash
    cd backend
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    
    pip install -r requirements.txt
    ```

3.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    ```

### Running the Simulation

1.  **Start the Backend**:
    ```bash
    # In the backend directory
    uvicorn app.main:app --reload
    ```

2.  **Start the Frontend**:
    ```bash
    # In the frontend directory
    npm run dev
    ```

3.  Open your browser to `http://localhost:5173` (or the port shown in your terminal).

## 🎮 Controls

-   **Left Click**: Select an agent to view details.
-   **Scroll**: Zoom in/out.
-   **Drag**: Pan the camera.
-   **Pause/Resume**: Use the button in the top-left corner.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).
