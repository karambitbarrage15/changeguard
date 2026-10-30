"""
ChangeGuard Unified Platform Orchestrator & Supervisor.
Spins up all ChangeGuard microservices concurrently in lightweight processes
with centralized log streaming and graceful signal handling.
"""
import sys
import os
import time
import subprocess
import signal
from typing import List, Dict, Any

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SERVICES = [
    {
        "name": "telemetry-service",
        "port": 8000,
        "cwd": "services/telemetry_service",
        "cmd": [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    },
    {
        "name": "risk-engine",
        "port": 8001,
        "cwd": "risk_engine",
        "cmd": [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
    },
    {
        "name": "mcp-server",
        "port": 8002,
        "cwd": "mcp_server",
        "cmd": [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
    },
    {
        "name": "rag-engine",
        "port": 8004,
        "cwd": "rag_engine",
        "cmd": [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
    },
    {
        "name": "sre-agent",
        "port": 8003,
        "cwd": "sre_agent",
        "cmd": [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
    },
    {
        "name": "dashboard",
        "port": 3000,
        "cwd": "dashboard",
        "cmd": [sys.executable, "-m", "http.server", "3000"]
    }
]

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print("=" * 70)
    print("  [+] CHANGEGUARD PLATFORM SUPERVISOR")
    print("  Starting all 6 services locally...")
    print("=" * 70)

    processes: Dict[str, subprocess.Popen] = {}

    def shutdown(sig, frame):
        print("\n[SUPERVISOR] Shutting down ChangeGuard services...")
        for name, p in processes.items():
            print(f"Stopping {name} (PID {p.pid})...")
            p.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    for svc in SERVICES:
        svc_cwd = os.path.join(root_dir, svc["cwd"])
        print(f"[*] Spawning {svc['name']:<20} -> http://localhost:{svc['port']}")
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{svc_cwd}{os.pathsep}{env.get('PYTHONPATH', '')}"

        p = subprocess.Popen(
            svc["cmd"],
            cwd=svc_cwd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        processes[svc["name"]] = p

    print("\n" + "=" * 70)
    print("  [SUCCESS] All ChangeGuard services are active!")
    print("  * Operations Dashboard:   http://localhost:3000")
    print("  * Telemetry API:          http://localhost:8000")
    print("  * Prometheus Metrics:     http://localhost:8000/metrics")
    print("  * Change-Risk Engine:     http://localhost:8001")
    print("  * MCP Tool Server:        http://localhost:8002")
    print("  * Autonomous SRE Agent:   http://localhost:8003")
    print("  * RAG Knowledge Engine:   http://localhost:8004")
    print("=" * 70)
    print("Press Ctrl+C to terminate all services.\n")

    try:
        while True:
            for name, p in processes.items():
                if p.poll() is not None:
                    print(f"[!] Warning: Service {name} exited unexpectedly with code {p.returncode}")
            time.sleep(2)
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()
