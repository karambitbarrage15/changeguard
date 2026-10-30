"""
ChangeGuard Pre-Deployment Change-Risk Analysis Engine API.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from app.diff_parser import DiffParser
from app.blast_radius import BlastRadiusAnalyzer
from app.scorer import RiskScorer

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "risk-engine", "message": "%(message)s"}'
)
logger = logging.getLogger("changeguard.risk_engine")

app = FastAPI(
    title="ChangeGuard - Change-Risk Analysis Engine",
    description="Analyzes Pull Requests and diffs for blast-radius, deployment safety, and regression risks",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RiskAnalysisRequest(BaseModel):
    diff: str = Field(..., description="Git unified diff text")
    commit_message: Optional[str] = Field(default="Update telemetry pipeline")
    author: Optional[str] = Field(default="engineer@automotive.io")
    branch: Optional[str] = Field(default="feature/telemetry-optimization")

SAMPLE_DIFFS = {
    "unbounded_query": {
        "title": "High Risk: Unbounded Query & Sync Sleep",
        "commit_message": "feat(telemetry): add batch historical vehicle lookups",
        "diff": """diff --git a/services/telemetry_service/app/telemetry.py b/services/telemetry_service/app/telemetry.py
--- a/services/telemetry_service/app/telemetry.py
+++ b/services/telemetry_service/app/telemetry.py
@@ -35,6 +35,14 @@ class TelemetryStore:
     def get_vehicle_history(self, vin: str):
+        # Query all records without index or pagination
+        query = "SELECT * FROM vehicle_events WHERE vin = '" + vin + "'"
+        import time
+        time.sleep(2.5) # Wait for buffer flush
+        cursor.execute(query)
+        return cursor.fetchall()
"""
    },
    "memory_leak_buffer": {
        "title": "Critical Risk: Unbounded Global Memory Buffer",
        "commit_message": "perf(cache): store uncompressed vehicle coordinates in memory",
        "diff": """diff --git a/services/telemetry_service/app/telemetry.py b/services/telemetry_service/app/telemetry.py
--- a/services/telemetry_service/app/telemetry.py
+++ b/services/telemetry_service/app/telemetry.py
@@ -12,4 +12,12 @@
+global_coordinate_cache = []
+
 def ingest(telemetry):
+    # Store uncompressed coordinates indefinitely
+    chunk = bytearray(50 * 1024 * 1024) # 50MB chunk
+    global_coordinate_cache.append(chunk)
     return {"status": "stored"}
"""
    },
    "safe_docs": {
        "title": "Low Risk: Documentation & Typo Fix",
        "commit_message": "docs(readme): update API endpoint documentation and telemetry examples",
        "diff": """diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -10,3 +10,5 @@
-### Old Telemetry Specs
+### Connected-Vehicle Telemetry Specifications
+All requests require standard JSON payload with VIN and GPS coordinates.
"""
    }
}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "risk-engine", "version": "1.0.0"}

@app.post("/risk/analyze")
def analyze_risk(payload: RiskAnalysisRequest):
    if not payload.diff.strip():
        raise HTTPException(status_code=400, detail="Diff cannot be empty")

    # 1. Parse Diff
    diff_data = DiffParser.parse(payload.diff)

    # 2. Evaluate Blast Radius & Topology
    blast_radius = BlastRadiusAnalyzer.evaluate(diff_data["categories"], diff_data["files"])

    # 3. Score Risk
    score_report = RiskScorer.evaluate(diff_data, payload.diff, payload.commit_message)

    logger.info(f"Analyzed PR change: score={score_report['risk_score']} tier={score_report['risk_tier']}")

    return {
        "commit_message": payload.commit_message,
        "author": payload.author,
        "branch": payload.branch,
        "diff_metrics": {
            "total_files": diff_data["total_files"],
            "added_lines": diff_data["total_added"],
            "deleted_lines": diff_data["total_deleted"],
            "categories": diff_data["categories"],
            "files": diff_data["files"]
        },
        "blast_radius": blast_radius,
        "risk_assessment": score_report
    }

@app.get("/risk/samples")
def get_samples():
    return SAMPLE_DIFFS
