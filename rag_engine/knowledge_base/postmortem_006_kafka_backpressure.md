# Post-Mortem 006: P2 Kafka Partition Rebalance Leading to Fleet Ingestion Backpressure

**Incident Date:** 2026-09-02  
**Severity:** P2 - Event Lag  
**Affected Service:** connected-vehicle-telemetry  
**Symptoms:** 
- Consumer lag exceeded 50,000 unread vehicle messages
- Telemetry buffer memory increased
- Prometheus alert: `CriticalMemoryExhaustion`

## Root Cause
A misconfigured partition assignment strategy caused a constant rebalance storm across Kafka consumer groups.

## Remediation & Recovery Steps
1. Reverted consumer group config to cooperative sticky assignor.
2. Flushed backlogged consumer partitions.

## Verification
Consumer lag returned to < 100 messages within 3 minutes.
