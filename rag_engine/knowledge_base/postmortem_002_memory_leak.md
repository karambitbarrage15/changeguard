# Post-Mortem 002: P1 Unbounded In-Memory Buffer Causing Pod OOM

**Incident Date:** 2026-05-18  
**Severity:** P1 - Critical Outage  
**Affected Service:** connected-vehicle-telemetry  
**Symptoms:** 
- Memory consumption climbed steadily from 180MB to 1.8GB over 30 minutes
- Kubernetes OOMKilled events on telemetry pods
- Prometheus alert: `CriticalMemoryExhaustion`

## Root Cause
A developer introduced an unconstrained global list `memory_buffer = []` to cache raw vehicle coordinate bytearrays without eviction policy, LRU limits, or TTL.

## Remediation & Recovery Steps
1. Executed rolling restart and GitOps rollback to release `v2.4.0-stable`.
2. Replaced raw memory buffer with bounded Redis ring buffer with 10MB maximum capacity.
3. Added Prometheus memory threshold alert trigger at 500MB.

## Verification
Memory leveled off at 145MB with stable resident set size (RSS).
