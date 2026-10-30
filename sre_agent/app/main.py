"""
ChangeGuard AI SRE Agent API.
Coordinates autonomous incident investigation, root cause diagnosis, and recovery.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from app.agent import sre_agent

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "sre-agent", "message": "%(message)s"}'
)
logger = logging.getLogger("changeguard.sre_agent_api")

app = FastAPI(
    title="ChangeGuard - AI SRE Agent",
    description="Autonomous incident investigation and remediation agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvestigateRequest(BaseModel):
    trigger: Optional[str] = Field(default="Automated Prometheus Alert: HighLatencyDegradation")

class RollbackRequest(BaseModel):
    incident_id: str = Field(..., description="ID of incident to roll back")

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "sre-agent",
        "agent_state": sre_agent.current_state,
        "investigations_completed": len(sre_agent.investigation_history)
    }

@app.get("/agent/status")
def get_status():
    return {
        "state": sre_agent.current_state,
        "total_events": len(sre_agent.live_events),
        "latest_incident": sre_agent.investigation_history[-1] if sre_agent.investigation_history else None
    }

@app.get("/agent/events")
def get_live_events():
    """Stream of agent thought process and tool execution events."""
    return {"events": sre_agent.live_events}

@app.post("/agent/investigate")
def trigger_investigation(req: InvestigateRequest):
    logger.info(f"Triggering autonomous investigation: {req.trigger}")
    report = sre_agent.run_investigation(req.trigger)
    return report

@app.post("/agent/rollback")
def execute_rollback(req: RollbackRequest):
    logger.info(f"Executing rollback approval for {req.incident_id}")
    result = sre_agent.execute_rollback(req.incident_id)
    return result

@app.get("/agent/history")
def get_history():
    return {
        "count": len(sre_agent.investigation_history),
        "history": sre_agent.investigation_history
    }
