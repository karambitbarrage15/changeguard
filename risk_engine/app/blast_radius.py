"""
Blast Radius and Dependency Topology Analyzer.
"""
from typing import Dict, Any, List

class BlastRadiusAnalyzer:
    SERVICE_GRAPH = {
        "connected-vehicle-telemetry": {
            "downstream": ["fleet-management-api", "battery-health-analyzer", "geofencing-alert-engine"],
            "upstream": ["mqtt-broker", "kafka-telemetry-topic"],
            "criticality": "HIGH"
        },
        "database": {
            "downstream": ["connected-vehicle-telemetry", "fleet-management-api", "user-auth-service"],
            "upstream": ["postgresql-cluster"],
            "criticality": "CRITICAL"
        },
        "infra": {
            "downstream": ["all-microservices"],
            "upstream": ["kubernetes-ingress", "aws-vpc"],
            "criticality": "CRITICAL"
        },
        "security": {
            "downstream": ["api-gateway", "telemetry-ingest"],
            "upstream": ["vault-secrets-manager"],
            "criticality": "HIGH"
        }
    }

    @classmethod
    def evaluate(cls, categories: List[str], changed_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        affected_services = set()
        highest_criticality = "LOW"
        graph_nodes = []
        graph_edges = []

        # Target node
        graph_nodes.append({"id": "pr-change", "label": "PR Changes", "type": "origin", "status": "modified"})

        for cat in categories:
            if cat in cls.SERVICE_GRAPH:
                info = cls.SERVICE_GRAPH[cat]
                affected_services.update(info["downstream"])
                if info["criticality"] == "CRITICAL":
                    highest_criticality = "CRITICAL"
                elif info["criticality"] == "HIGH" and highest_criticality != "CRITICAL":
                    highest_criticality = "HIGH"

        if not affected_services:
            affected_services = {"connected-vehicle-telemetry"}
            highest_criticality = "MEDIUM"

        for svc in affected_services:
            graph_nodes.append({"id": svc, "label": svc, "type": "service", "status": "affected"})
            graph_edges.append({"from": "pr-change", "to": svc})

        return {
            "criticality_level": highest_criticality,
            "affected_services": sorted(list(affected_services)),
            "affected_fleets": ["fleet-california-01", "fleet-nevada-02", "fleet-texas-03"] if highest_criticality in ["HIGH", "CRITICAL"] else ["fleet-california-01"],
            "estimated_fleet_impact_pct": 100 if highest_criticality == "CRITICAL" else (40 if highest_criticality == "HIGH" else 10),
            "topology_graph": {
                "nodes": graph_nodes,
                "edges": graph_edges
            }
        }
