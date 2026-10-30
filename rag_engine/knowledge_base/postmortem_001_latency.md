# Post-Mortem 001: P1 Latency Degradation in California Fleet Ingestion

**Incident Date:** 2026-04-12  
**Severity:** P1 - Critical Degradation  
**Affected Service:** connected-vehicle-telemetry  
**Symptoms:** 
- p95 latency spiked from 45ms to 2800ms
- Prometheus alert: `HighLatencyDegradation`
- High queue backlog on telemetry ingestion endpoint `/telemetry`

## Root Cause
A recent commit added synchronous blocking call (`time.sleep(2.5)`) and an unindexed SQL query inside the telemetry ingestion pipeline during buffer flushes. This caused event loop worker starvation.

## Remediation & Recovery Steps
1. Immediate GitOps rollback via ArgoCD to release `v2.4.0-stable`.
2. Flushed trapped in-memory pending vehicle event queues.
3. Added asynchronous non-blocking worker pool for batch persistence.

## Verification
Latency dropped back to 38ms within 45 seconds of rollback. 0 dropped packets.
