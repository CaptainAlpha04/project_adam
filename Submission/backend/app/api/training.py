from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..rl.training_manager import TrainingManager

router = APIRouter(prefix="/train", tags=["training"])

class TrainRequest(BaseModel):
    scenario: str
    generations: int = 10

@router.post("/start")
async def start_training(req: TrainRequest):
    success = TrainingManager.start_training(req.scenario, req.generations)
    if not success:
        raise HTTPException(status_code=400, detail="Training already in progress")
    return {"status": "started", "scenario": req.scenario}

@router.post("/stop")
async def stop_training():
    TrainingManager.stop_training()
    return {"status": "stopping"}

@router.get("/status")
async def get_status():
    is_running = TrainingManager.thread is not None and TrainingManager.thread.is_alive()
    return {"running": is_running}
