# Post-Mortem 004: P1 Erroneous Rate Limit Configuration Rejecting 50% of Ingestion

**Incident Date:** 2026-07-22  
**Severity:** P1 - Widespread Ingestion Failure  
**Affected Service:** connected-vehicle-telemetry  
**Symptoms:** 
- Ingestion endpoints failing with 500/429 HTTP status codes
- Error rate skyrocketed to 50%
- Prometheus alert: `HighErrorRateSpike`

## Root Cause
A bad Helm values configuration deployment inadvertently applied a test token-bucket rate limiter of 5 requests/sec to the production telemetry gateway.

## Remediation & Recovery Steps
1. Immediate GitOps sync rollback to revision `v2.4.0-stable`.
2. Verified telemetry ingress traffic returned to 450 req/sec without throttles.

## Verification
All fleet vehicles re-established live websocket/HTTP connections. Error rate 0%.
