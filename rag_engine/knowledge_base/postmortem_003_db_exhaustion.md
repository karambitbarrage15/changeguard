# Post-Mortem 003: P2 Postgres Connection Pool Saturation Following Ingestion Spike

**Incident Date:** 2026-06-03  
**Severity:** P2 - Degraded Ingestion  
**Affected Service:** connected-vehicle-telemetry  
**Symptoms:** 
- `remaining_connections: 0` error in PostgreSQL logs
- Telemetry API throwing `500 Internal Server Error` on 35% of POST requests
- Prometheus alert: `HighErrorRateSpike`

## Root Cause
Connection pool size was hardcoded to 10 connections without connection checkout timeout or pooling reuse via PgBouncer.

## Remediation & Recovery Steps
1. Scaled down rogue pods and restarted connection proxy.
2. Rolled back configuration change and enabled PgBouncer connection multiplexing.

## Verification
Database connections stabilized at 22/100 connections. Error rate dropped to 0.0%.
