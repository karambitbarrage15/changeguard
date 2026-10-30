"""
ChangeGuard End-to-End System Integration Test Suite.
Validates all subsystems: Telemetry, Chaos, Risk Engine, MCP Server, RAG Engine, and SRE Agent.
"""
import sys
import os
import unittest

# Setup python path for all microservices
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "services", "telemetry_service"))
sys.path.insert(0, os.path.join(BASE_DIR, "risk_engine"))
sys.path.insert(0, os.path.join(BASE_DIR, "mcp_server"))
sys.path.insert(0, os.path.join(BASE_DIR, "rag_engine"))
sys.path.insert(0, os.path.join(BASE_DIR, "sre_agent"))

class TestChangeGuardEndToEnd(unittest.TestCase):

    def test_01_telemetry_and_chaos(self):
        """Test connected vehicle telemetry models and chaos state transitions."""
        from services.telemetry_service.app.telemetry import telemetry_store
        from services.telemetry_service.app.chaos import chaos_controller

        # 1. Ingestion
        sample = telemetry_store.generate_sample(42)
        res = telemetry_store.ingest(sample)
        self.assertEqual(res["status"], "ingested")
        self.assertGreaterEqual(telemetry_store.get_vehicle_count(), 1)

        # 2. Chaos Injection
        chaos_controller.inject_latency(1500)
        status = chaos_controller.get_status()
        self.assertEqual(status["latency_ms"], 1500)
        self.assertTrue(status["is_degraded"])

        # 3. Chaos Reset
        chaos_controller.reset()
        status_after = chaos_controller.get_status()
        self.assertEqual(status_after["latency_ms"], 0.0)
        self.assertFalse(status_after["is_degraded"])

    def test_02_change_risk_engine(self):
        """Test diff parsing, blast radius, and risk scoring."""
        from risk_engine.app.diff_parser import DiffParser
        from risk_engine.app.blast_radius import BlastRadiusAnalyzer
        from risk_engine.app.scorer import RiskScorer

        sample_diff = """diff --git a/services/telemetry_service/app/telemetry.py b/services/telemetry_service/app/telemetry.py
--- a/services/telemetry_service/app/telemetry.py
+++ b/services/telemetry_service/app/telemetry.py
@@ -10,3 +10,6 @@
+def fetch_all():
+    time.sleep(3.0)
+    return cursor.execute("SELECT * FROM events")
"""
        parsed = DiffParser.parse(sample_diff)
        self.assertGreater(parsed["total_added"], 0)
        self.assertIn("core_telemetry", parsed["categories"])

        blast = BlastRadiusAnalyzer.evaluate(parsed["categories"], parsed["files"])
        self.assertIn("connected-vehicle-telemetry", blast["affected_services"])

        score_report = RiskScorer.evaluate(parsed, sample_diff, "feat: test query")
        self.assertGreaterEqual(score_report["risk_score"], 30)
        self.assertIn(score_report["risk_tier"], ["MEDIUM", "HIGH", "CRITICAL"])

    def test_03_rag_retrieval(self):
        """Test RAG knowledge base indexing and similarity retrieval."""
        from rag_engine.app.retriever import RAGRetriever

        kb_dir = os.path.join(BASE_DIR, "rag_engine", "knowledge_base")
        retriever = RAGRetriever(kb_dir)
        docs = retriever.get_all()
        self.assertGreaterEqual(len(docs), 5)

        matches = retriever.retrieve("latency degradation timeout alert", top_k=2)
        self.assertGreater(len(matches), 0)
        self.assertTrue(any("Latency" in m["title"] or "Timeout" in m["title"] or "Synchronous" in m["title"] for m in matches))

    def test_04_mcp_server_tools(self):
        """Test MCP tools registry."""
        from mcp_server.app.main import TOOL_REGISTRY
        self.assertIn("git_log", TOOL_REGISTRY)
        self.assertIn("query_prometheus", TOOL_REGISTRY)
        self.assertIn("trigger_rollback", TOOL_REGISTRY)
        self.assertIn("verify_health", TOOL_REGISTRY)

        # Call git_log tool
        commits = TOOL_REGISTRY["git_log"](limit=2)
        self.assertIsInstance(commits, list)
        self.assertGreater(len(commits), 0)

    def test_05_sre_agent_investigation_loop(self):
        """Test autonomous SRE investigation loop and recovery."""
        from sre_agent.app.agent import sre_agent

        # Run investigation
        report = sre_agent.run_investigation("E2E Test Incident")
        self.assertEqual(report["status"], "INVESTIGATION_COMPLETE")
        self.assertIn("root_cause_analysis", report)
        self.assertIn("blast_radius", report)
        self.assertGreater(len(sre_agent.live_events), 3)

        # Execute rollback
        recovery = sre_agent.execute_rollback(report["incident_id"])
        self.assertEqual(recovery["status"], "RECOVERED")
        self.assertTrue(recovery["verification"]["healthy"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
