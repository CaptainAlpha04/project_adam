import uvicorn
import os
import sys

if __name__ == "__main__":
    # Ensure current directory (root) is in sys.path
    # This allows 'backend' to be imported as a top-level package
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    print(f"Starting Server from {os.getcwd()}")
    print("Project Adam: Agent Rebirth Backend")
    
    # Run Uvicorn
    # reload=True works because re-running this script re-adds the path
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
