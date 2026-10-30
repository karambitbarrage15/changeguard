# 🛡️ ChangeGuard

> **AI-Powered Change-Intelligence & Autonomous SRE Platform**  
> *Pre-Deployment Blast-Radius Prediction · MCP Tool Protocol · Vectorized RAG Playbooks · Automated GitOps Rollback*

---

## 📋 Overview

**ChangeGuard** is a production-grade DevOps + AI platform engineered to protect critical real-time infrastructure. Using a connected-vehicle telemetry streaming pipeline as its target production system, ChangeGuard operates across two mission-critical phases:

1. **Pre-Deployment Safety (Change-Risk Engine):** Analyzes incoming Pull Requests and Git diffs to compute risk scores (0–100), identify dangerous patterns (unbounded queries, synchronous sleeps, memory leaks), and calculate blast-radius topology before changes hit production.
2. **Post-Deployment Incident Remediation (Autonomous AI SRE Agent):** When telemetry degrades or Prometheus alerts fire, an autonomous AI SRE Agent leverages the **Model Context Protocol (MCP)** and a **Vectorized RAG Knowledge Base** to inspect live metrics, scan container logs, correlate recent Git commits, pinpoint root cause, and execute human-approved GitOps rollbacks with automated recovery verification.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph PreDeployment ["1. Pre-Deployment Gate"]
        PR["Git Pull Request / Diff"] --> RiskEngine["Risk Analysis Engine (:8001)"]
        RiskEngine --> Blast["Blast Radius & Topology"]
        RiskEngine --> Score["Risk Score & Canary Strategy"]
    end

    subgraph Runtime ["2. Runtime & Telemetry Pipeline"]
        Telemetry["Connected-Vehicle Telemetry (:8000)"] --> Prom["Prometheus (:9090)"]
        Chaos["Chaos Injection Studio"] -.->|inject faults| Telemetry
        Prom --> Alerts["Degradation Detection Rules"]
    end

    subgraph AutonomousSRE ["3. AI SRE Agent & Investigation"]
        Alerts --> Agent["Autonomous SRE Agent (:8003)"]
        Agent <-->|MCP Protocol| MCP["MCP Tool Server (:8002)"]
        MCP --> GitTools["Git History & Diffs"]
        MCP --> PromTools["Prometheus PromQL"]
        MCP --> LogTools["Container Logs"]
        MCP --> ContainerTools["Docker / Health Probes"]
        Agent <-->|Semantic Search| RAG["Vectorized RAG Engine (:8004)"]
        RAG --> Playbooks[("Historical Post-Mortems")]
        Agent --> RCA["Root Cause Analysis (RCA)"]
    end

    subgraph OpsCenter ["4. Operations Command Center (:3000)"]
        OpsCenter --> LiveTelemetry["Live Fleet Stream"]
        OpsCenter --> RiskPanel["Diff Risk Studio"]
        OpsCenter --> ThoughtStream["Live Agent Thought Stream"]
        OpsCenter --> RollbackApproval["Human-in-the-Loop Rollback"]
    end

    Score --> OpsCenter
    RCA --> OpsCenter
```

---

## 📦 Components Breakdown

| Service | Port | Description |
|---|---|---|
| **`telemetry-service`** | `8000` | Connected-vehicle telemetry ingestion (`/telemetry`) with Prometheus metrics (`/metrics`) and chaos engineering hooks (`/chaos/*`). Runs a background fleet simulator generating continuous live vehicle data. |
| **`risk-engine`** | `8001` | Unified diff parser, blast-radius dependency evaluator, pattern classifier, and risk scoring engine (`/risk/analyze`). |
| **`mcp-server`** | `8002` | Model Context Protocol server exposing `git_log`, `git_diff_commit`, `query_prometheus`, `search_logs`, `inspect_container`, and `trigger_rollback`. |
| **`rag-engine`** | `8004` | Vectorized incident knowledge base with TF-IDF semantic embeddings indexing 8 real-world production incident post-mortems (`/rag/query`). |
| **`sre-agent`** | `8003` | Autonomous incident orchestrator executing multi-step diagnostic plans, reasoning over evidence, matching historical playbooks, and synthesizing root-cause reports (`/agent/investigate`). |
| **`dashboard`** | `3000` | Dark-mode glassmorphic single-pane-of-glass operations center featuring live fleet telemetry, chaos studio, interactive diff analyzer, and real-time agent terminal. |
| **`prometheus`** | `9090` | Time-series metrics collection with pre-configured degradation alert rules (`prometheus/alert_rules.yml`). |
| **`grafana`** | `3001` | Pre-provisioned telemetry health dashboard (`grafana/provisioning/`). |

---

## 🚀 Quickstart

### Method 1: Local Direct Runner (Zero Docker Dependency)
You can launch the entire 6-service platform locally with Python:

```bash
# 1. Install dependencies
pip install -r services/telemetry_service/requirements.txt
pip install -r risk_engine/requirements.txt
pip install -r mcp_server/requirements.txt
pip install -r rag_engine/requirements.txt
pip install -r sre_agent/requirements.txt

# 2. Launch all services concurrently
python orchestrator/run_platform.py
```

Open your browser to:
👉 **`http://localhost:3000`**

---

### Method 2: Docker Compose
If Docker Desktop is running on your machine:

```bash
docker compose up --build
```

---

## 🧪 Automated Test Suite

ChangeGuard includes a comprehensive end-to-end integration test suite:

```bash
python test_e2e.py
```

Verifies:
- `test_01_telemetry_and_chaos`: Telemetry ingestion, model serialization, and chaos state transitions.
- `test_02_change_risk_engine`: Diff parsing, dependency graph traversal, blast-radius mapping, and risk scoring.
- `test_03_rag_retrieval`: Vector space indexing and semantic search over markdown post-mortems.
- `test_04_mcp_server_tools`: MCP tool registry dispatch, git inspection, and container probes.
- `test_05_sre_agent_investigation_loop`: Autonomous incident planner execution, MCP tool calls, RAG matching, RCA synthesis, and rollback verification.

---

## 🎮 Interactive Demo Walkthrough

### 1. Pre-Deployment Risk Studio (Tab 2)
1. Navigate to **Pre-Deploy Change Risk**.
2. Select one of the pre-loaded sample diffs:
   * **Unbounded Query & Sleep:** High-risk blocking sleep in telemetry pipeline.
   * **Memory Buffer Leak:** Critical-risk unbounded global array allocation.
   * **Safe Documentation:** Low-risk markdown documentation update.
3. Click **Run AI Change-Risk Analysis**.
4. Observe:
   * Animated SVG Risk Score Gauge (0–100).
   * Status Pill (`BLOCKED`, `REQUIRES_HUMAN_SIGN_OFF`, `AUTO_APPROVED`).
   * Canary rollout strategy (e.g., *Multi-stage Canary 1% -> 5% -> 25%*).
   * Blast-radius affected services and topology chips.
   * Actionable SRE safety recommendations.

### 2. Runtime Telemetry & Chaos Studio (Tab 1)
1. Navigate to **Runtime & Chaos Studio**.
2. View real-time incoming vehicle telemetry streaming every 2 seconds (VIN, speed, battery state of charge, firmware).
3. Under **Chaos Engineering Injection Studio**, click **Inject Latency Spike (+2500ms)**.
4. Watch metrics immediately reflect the incident:
   * p95 Latency turns red (> 2500ms).
   * Top bar status changes to `INCIDENT DEGRADATION`.
   * A notification badge appears on the **Autonomous AI SRE Agent** tab.

### 3. Autonomous AI SRE Investigation (Tab 3)
1. Switch to the **Autonomous AI SRE Agent** tab.
2. Click **Trigger Autonomous Investigation** (or let it auto-trigger from the alert).
3. Watch the live terminal thought stream in real-time:
   * `[THOUGHT]` Checking Prometheus alerts...
   * `[MCP TOOL]` Retrieved active alert: `HighLatencyDegradation`
   * `[MCP TOOL]` Queried PromQL metric counters
   * `[MCP TOOL]` Scanned container error logs
   * `[MCP TOOL]` Retrieved recent Git commits via `git_log`
   * `[MCP TOOL]` Analyzed code diff of HEAD revision
   * `[MCP TOOL]` Matched historical incident in RAG knowledge base
   * `[AI DEDUCTION]` Root Cause Confirmed!
4. Review the generated **Root Cause Analysis (RCA)** card.
5. Click **Approve & Execute GitOps Rollback**.
6. The agent calls MCP tool `trigger_rollback`, executes ArgoCD revision reset, runs MCP tool `verify_health`, and displays **Recovery Verified** with latency normalized back to `< 50ms`.

---

## 🔧 Environment Configuration (`.env`)

```ini
# Core Service Ports
TELEMETRY_PORT=8000
RISK_ENGINE_PORT=8001
MCP_SERVER_PORT=8002
SRE_AGENT_PORT=8003
RAG_ENGINE_PORT=8004
DASHBOARD_PORT=3000

# LLM Provider (Optional - works fully offline via deterministic heuristic fallback)
LLM_PROVIDER=gemini
GEMINI_API_KEY=
OPENAI_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 📜 Systematic Git Commit History

The repository has been constructed through systematic, atomic commits:

1. `8756a70` — `chore(infra): initialize repository scaffolding, docker compose, prometheus & grafana configs`
2. `e309f7d` — `feat(telemetry): implement connected-vehicle telemetry service with prometheus metrics and chaos engineering hooks`
3. `2fb8978` — `feat(risk-engine): implement change-risk analysis engine with diff parser, blast-radius topology & scoring`
4. `433a350` — `feat(mcp-rag): implement MCP tool server & vectorized RAG engine with incident post-mortems`
5. `ab32e30` — `feat(sre-agent): implement autonomous AI SRE agent with incident planner, MCP investigation loop, RAG correlation & rollback`
6. `e46051b` — `feat(dashboard): implement operations command center with live chaos console, risk studio, and agent thought stream`
7. `...` — `feat(orchestrator): add supervisor, end-to-end test suite, and comprehensive documentation`

---

## 📄 License
MIT License. Built for Production DevOps & AI Engineering.
