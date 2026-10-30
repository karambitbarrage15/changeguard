"""
ChangeGuard MCP (Model Context Protocol) Server.
Provides standardized tool execution for the autonomous AI SRE agent.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from app.tools.git_tools import git_log, git_diff_commit, git_blame
from app.tools.prometheus_tools import query_prometheus, get_active_alerts
from app.tools.log_tools import search_logs
from app.tools.container_tools import list_containers, inspect_container, trigger_rollback, verify_health

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "mcp-server", "message": "%(message)s"}'
)
logger = logging.getLogger("changeguard.mcp")

app = FastAPI(
    title="ChangeGuard - MCP Server",
    description="Model Context Protocol Server exposing Git, Prometheus, Container, and Log tools to AI Agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registry of tools
TOOL_REGISTRY = {
    "git_log": git_log,
    "git_diff_commit": git_diff_commit,
    "git_blame": git_blame,
    "query_prometheus": query_prometheus,
    "get_active_alerts": get_active_alerts,
    "search_logs": search_logs,
    "list_containers": list_containers,
    "inspect_container": inspect_container,
    "trigger_rollback": trigger_rollback,
    "verify_health": verify_health,
}

TOOL_SCHEMAS = [
    {
        "name": "get_active_alerts",
        "description": "Checks Prometheus and telemetry service for currently firing alerts and degradation conditions",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "query_prometheus",
        "description": "Executes a PromQL metric query against Prometheus or telemetry metrics endpoint",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "PromQL query string"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_logs",
        "description": "Searches recent application and system logs for error traces and stack anomalies",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Optional keyword or error string to filter by"},
                "level": {"type": "string", "description": "Log level (INFO, WARNING, ERROR)", "default": "ERROR"}
            }
        }
    },
    {
        "name": "git_log",
        "description": "Retrieves recent commits with authors, timestamps, and commit messages",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of commits to return", "default": 5}
            }
        }
    },
    {
        "name": "git_diff_commit",
        "description": "Inspects the exact unified diff introduced by a specific commit hash",
        "parameters": {
            "type": "object",
            "properties": {
                "commit_hash": {"type": "string", "description": "Commit hash to inspect, default HEAD"}
            }
        }
    },
    {
        "name": "list_containers",
        "description": "Lists all active platform microservices and containers with status and ports",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "inspect_container",
        "description": "Inspects resource utilization, memory leak metrics, and health of a specific container",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Container or service name"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "trigger_rollback",
        "description": "Executes an automated GitOps rollback to restore a service to its last stable release revision",
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string", "description": "Name of service to roll back", "default": "connected-vehicle-telemetry"},
                "target_version": {"type": "string", "description": "Target git tag or release", "default": "v2.4.0-stable"}
            }
        }
    },
    {
        "name": "verify_health",
        "description": "Verifies that service latency, error rates, and memory usage have recovered post-rollback",
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string", "description": "Service name to verify"}
            }
        }
    }
]

class ToolCallRequest(BaseModel):
    tool: str = Field(..., description="Tool name to execute")
    arguments: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Arguments to pass to tool")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "mcp-server", "registered_tools": len(TOOL_REGISTRY)}

@app.get("/mcp/tools")
def get_tools():
    """Return list of all registered MCP tool specifications."""
    return {"tools": TOOL_SCHEMAS}

@app.post("/mcp/call")
def call_tool(req: ToolCallRequest):
    """Execute a registered tool and return structured output."""
    tool_fn = TOOL_REGISTRY.get(req.tool)
    if not tool_fn:
        raise HTTPException(status_code=404, detail=f"Tool '{req.tool}' not found in MCP registry")

    try:
        logger.info(f"Executing MCP tool '{req.tool}' with args {req.arguments}")
        args = req.arguments or {}
        result = tool_fn(**args)
        return {
            "tool": req.tool,
            "status": "success",
            "output": result
        }
    except Exception as e:
        logger.error(f"Error executing MCP tool '{req.tool}': {e}")
        return {
            "tool": req.tool,
            "status": "error",
            "error": str(e)
        }
