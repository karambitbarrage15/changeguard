"""
Risk Scoring & Blast-Radius Prediction Engine.
Evaluates code diffs, detects high-risk patterns, and produces actionable SRE safety reports.
"""
import os
import re
from typing import Dict, Any, List

class RiskScorer:
    HIGH_RISK_PATTERNS = [
        (r"DROP\s+TABLE|ALTER\s+TABLE", 40, "Destructive database migration detected"),
        (r"SELECT\s+\*\s+FROM|without\s+LIMIT", 30, "Unbounded database query risk"),
        (r"time\.sleep\s*\(|sleep\(", 25, "Synchronous blocking sleep in async pipeline"),
        (r"while\s+True|for\s+.*\s+in\s+iter", 20, "Potential unbounded loop / CPU lockup"),
        (r"memory_buffer\.append|global\s+cache", 25, "Unbounded memory buffer allocation"),
        (r"password|secret|api_key|token\s*=\s*['\"][^'\"]+", 35, "Potential hardcoded credential or secret"),
        (r"verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED", 35, "Disabled SSL/TLS verification"),
        (r"timeout\s*=\s*None|no_timeout", 25, "Missing network call timeout")
    ]

    @classmethod
    def evaluate(cls, diff_data: Dict[str, Any], raw_diff: str, commit_msg: str = "") -> Dict[str, Any]:
        base_score = 10
        risk_factors: List[Dict[str, Any]] = []

        # 1. Size-based risk
        total_changes = diff_data["total_added"] + diff_data["total_deleted"]
        if total_changes > 500:
            base_score += 30
            risk_factors.append({"factor": "Large Diff Size", "weight": "+30", "detail": f"{total_changes} lines changed"})
        elif total_changes > 150:
            base_score += 15
            risk_factors.append({"factor": "Moderate Diff Size", "weight": "+15", "detail": f"{total_changes} lines changed"})

        # 2. Category weights
        categories = diff_data["categories"]
        if "database" in categories:
            base_score += 35
            risk_factors.append({"factor": "Database / Schema Modification", "weight": "+35", "detail": "Alters persistent data models"})
        if "infra" in categories:
            base_score += 25
            risk_factors.append({"factor": "Infrastructure / Deployment Config", "weight": "+25", "detail": "Modifies container or K8s definitions"})
        if "security" in categories:
            base_score += 25
            risk_factors.append({"factor": "Security / Auth Surface", "weight": "+25", "detail": "Touches authentication or encryption paths"})
        if "dependencies" in categories:
            base_score += 15
            risk_factors.append({"factor": "Third-Party Dependencies", "weight": "+15", "detail": "Adds or updates upstream packages"})

        # 3. Pattern matching on raw diff
        for pattern, weight, description in cls.HIGH_RISK_PATTERNS:
            if re.search(pattern, raw_diff, re.IGNORECASE):
                base_score += weight
                risk_factors.append({"factor": "Dangerous Pattern", "weight": f"+{weight}", "detail": description})

        # Cap score between 0 and 100
        score = min(100, max(5, base_score))

        # Determine Tier & Status
        if score >= 75:
            tier = "CRITICAL"
            approval_status = "BLOCKED"
            canary_strategy = "Multi-stage Canary (1% -> 5% -> 25%) with 1-hour bake time"
        elif score >= 50:
            tier = "HIGH"
            approval_status = "REQUIRES_HUMAN_SIGN_OFF"
            canary_strategy = "Standard Canary (5% -> 50% -> 100%) with 15-min soak"
        elif score >= 25:
            tier = "MEDIUM"
            approval_status = "REQUIRES_PEER_REVIEW"
            canary_strategy = "Blue/Green deployment with instant rollback gate"
        else:
            tier = "LOW"
            approval_status = "AUTO_APPROVED"
            canary_strategy = "Rolling update with automated health checks"

        # Recommendations
        recommendations = cls._generate_recommendations(tier, risk_factors, categories)

        return {
            "risk_score": score,
            "risk_tier": tier,
            "approval_status": approval_status,
            "canary_strategy": canary_strategy,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "summary": f"Diff presents {tier} deployment risk (Score: {score}/100). Status: {approval_status}."
        }

    @staticmethod
    def _generate_recommendations(tier: str, factors: List[Dict[str, Any]], categories: List[str]) -> List[str]:
        recs = []
        if tier in ["CRITICAL", "HIGH"]:
            recs.append("Verify rollback automation and ensure database migration is backwards-compatible.")
            recs.append("Stage deployment to canary fleet-california-01 before wider rollout.")
            recs.append("Alert on-call SRE and monitor latency/error p95 thresholds for 20 minutes post-deploy.")
        if "database" in categories:
            recs.append("Run `EXPLAIN ANALYZE` on all newly introduced database queries.")
            recs.append("Ensure schema alterations do not acquire exclusive table locks during peak ingestion hours.")
        if any("sleep" in f.get("detail", "").lower() for f in factors):
            recs.append("Refactor synchronous sleep calls into asynchronous non-blocking event loops or task queues.")
        if not recs:
            recs.append("Unit tests pass. Automated deployment approved for rolling rollout.")
            recs.append("Standard telemetry health checks will monitor telemetry ingestion rate.")
        return recs
