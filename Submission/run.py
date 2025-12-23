import uvicorn
import os
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Project Adam Backend")
    parser.add_argument("--mode", type=str, choices=["heuristic", "rl"], default="heuristic", help="Simulation Mode: 'heuristic' (Legacy) or 'rl' (Trained Model)")
    args = parser.parse_args()

    # Set Environment Variable for main.py to read
    os.environ["PROJECT_ADAM_MODE"] = args.mode.upper()

    # Ensure current directory (root) is in sys.path
    # This allows 'backend' to be imported as a top-level package
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    print(f"Starting Server from {os.getcwd()}")
    print(f"Project Adam: Agent Rebirth Backend (MODE: {args.mode.upper()})")
    
    # Run Uvicorn
    # reload=True works because re-running this script re-adds the path
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
