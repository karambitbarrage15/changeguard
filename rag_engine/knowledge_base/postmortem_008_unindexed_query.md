# Post-Mortem 008: P2 Full Table Scan on Vehicle Events Table During Batch Lookups

**Incident Date:** 2026-10-05  
**Severity:** P2 - Database CPU Saturation  
**Affected Service:** connected-vehicle-telemetry  
**Symptoms:** 
- Latency increased to 2500ms on vehicle history lookups
- Database CPU at 98%
- Prometheus alert: `HighLatencyDegradation`

## Root Cause
A newly committed feature queried historical vehicle logs using `vin` and `timestamp` without a composite index on `(vin, timestamp)`.

## Remediation & Recovery Steps
1. Rolled back PR to stable revision.
2. Created composite index `idx_vehicle_events_vin_ts` concurrently.

## Verification
Query execution time dropped from 2400ms to 4ms. Database CPU normalized at 18%.
