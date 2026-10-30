# Post-Mortem 005: P1 Synchronous External Geocoding API Blocking Telemetry Workers

**Incident Date:** 2026-08-14  
**Severity:** P1 - Worker Thread Starvation  
**Affected Service:** connected-vehicle-telemetry  
**Symptoms:** 
- Worker thread pool saturation (100% thread utilization)
- Request timeout errors on client vehicle gateways
- Prometheus alert: `HighLatencyDegradation`

## Root Cause
A third-party reverse geocoding API was invoked synchronously on every GPS location update without circuit breaking or fallback caching.

## Remediation & Recovery Steps
1. Rolled back deployment to `v2.4.0-stable`.
2. Decoupled geocoding into an asynchronous Kafka consumer topic.

## Verification
Thread pool usage dropped from 100% to 14%. Latency p95 restored to 42ms.
