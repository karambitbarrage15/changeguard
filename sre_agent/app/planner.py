"""
Investigation Planner for ChangeGuard SRE Agent.
Formulates structured incident investigation plans.
"""
from typing import List, Dict, Any

class InvestigationPlanner:
    @staticmethod
    def create_plan(incident_hint: str = "") -> List[Dict[str, Any]]:
        return [
            {
                "step": 1,
                "action": "check_alerts",
                "tool": "get_active_alerts",
                "arguments": {},
                "goal": "Identify currently firing Prometheus and system alerts"
            },
            {
                "step": 2,
                "action": "query_metrics",
                "tool": "query_prometheus",
                "arguments": {"query": "changeguard_request_latency_seconds"},
                "goal": "Verify telemetry p95 latency, error rate, and memory trends"
            },
            {
                "step": 3,
                "action": "search_error_logs",
                "tool": "search_logs",
                "arguments": {"level": "ERROR"},
                "goal": "Scan logs for stack traces, chaos signatures, and exceptions"
            },
            {
                "step": 4,
                "action": "inspect_git_history",
                "tool": "git_log",
                "arguments": {"limit": 3},
                "goal": "Identify recent commits deployed prior to degradation onset"
            },
            {
                "step": 5,
                "action": "inspect_commit_diff",
                "tool": "git_diff_commit",
                "arguments": {"commit_hash": "HEAD"},
                "goal": "Examine line-by-line diff of the offending deployment"
            },
            {
                "step": 6,
                "action": "query_rag_knowledge",
                "goal": "Match symptoms against historical post-mortems and incident playbooks"
            },
            {
                "step": 7,
                "action": "synthesize_rca",
                "goal": "Synthesize Root Cause Analysis, blast-radius assessment, and rollback recommendation"
            }
        ]
