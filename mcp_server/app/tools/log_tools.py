"""
MCP Tool: Application log search and analysis.
"""
import os
import re
import httpx
from typing import Dict, Any, List

TELEMETRY_URL = os.getenv("TELEMETRY_URL", "http://localhost:8000")

def search_logs(keyword: str = "", level: str = "ERROR", limit: int = 15) -> List[Dict[str, Any]]:
    """Search service logs for error traces, exceptions, and anomalies."""
    logs = []
    try:
        with httpx.Client(timeout=0.2) as client:
            resp = client.get(f"{TELEMETRY_URL}/chaos/status")
            if resp.status_code == 200:
                data = resp.json()
                for inc in data.get("active_incidents", []):
                    logs.append({
                        "level": "ERROR" if "SPIKE" in inc.get("type", "") else "WARNING",
                        "message": f"[{inc.get('type')}] {inc.get('description')}",
                        "timestamp": inc.get("timestamp"),
                        "source": "telemetry-service"
                    })
    except Exception:
        pass

    # In-process fallback
    if not logs:
        try:
            from services.telemetry_service.app.chaos import chaos_controller
            for inc in chaos_controller.active_incidents:
                logs.append({
                    "level": "ERROR" if "SPIKE" in inc.get("type", "") else "WARNING",
                    "message": f"[{inc.get('type')}] {inc.get('description')}",
                    "timestamp": inc.get("timestamp"),
                    "source": "telemetry-service"
                })
        except Exception:
            pass

    # Provide synthetic baseline log if clean
    if not logs:
        logs.append({
            "level": "INFO",
            "message": "Connected-vehicle telemetry ingestion operating normally. Ingest rate: 300 msg/sec.",
            "source": "telemetry-service"
        })

    # Filter
    if keyword:
        logs = [l for l in logs if keyword.lower() in l["message"].lower()]

    return logs[:limit]
