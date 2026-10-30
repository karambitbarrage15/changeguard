# Post-Mortem 007: P1 Firmware Payload Parsing 500 Error Ingestion Spike

**Incident Date:** 2026-09-19  
**Severity:** P1 - Ingestion 500 Spike  
**Affected Service:** connected-vehicle-telemetry  
**Symptoms:** 
- Ingestion error rate spiked to 45% immediately following deployment
- Log traces: `KeyError: battery_chemistry_id`
- Prometheus alert: `HighErrorRateSpike`

## Root Cause
Release v2.4.1-rc2 expected a mandatory field `battery_chemistry_id` that was not yet populated by older vehicle firmware fleets.

## Remediation & Recovery Steps
1. Immediate automated rollback to `v2.4.0-stable`.
2. Updated schema validator to treat `battery_chemistry_id` as optional with fallback default.

## Verification
Error rate instantly dropped to 0.0% upon rollback verification.
