"""
Chaos Engineering Controller for ChangeGuard Target Service.
Allows simulating production degradation:
- Latency spikes
- 5xx Error spikes
- Memory leaks
- Process crashes
"""
import os
import sys
import time
import asyncio
import logging
from typing import Dict, Any, List

logger = logging.getLogger("changeguard.chaos")

class ChaosController:
    def __init__(self):
        self.latency_ms: float = 0.0
        self.error_rate: float = 0.0  # 0.0 to 1.0
        self.memory_buffer: List[bytearray] = []
        self.simulated_crash: bool = False
        self.active_incidents: List[Dict[str, Any]] = []

    def inject_latency(self, ms: float) -> Dict[str, Any]:
        self.latency_ms = max(0.0, float(ms))
        incident = {
            "type": "LATENCY_SPIKE",
            "value": f"{self.latency_ms}ms",
            "timestamp": time.time(),
            "description": f"Artificially injected {self.latency_ms}ms delay on request pipeline"
        }
        self.active_incidents.append(incident)
        logger.warning(f"[CHAOS] Latency injected: {self.latency_ms}ms")
        return incident

    def inject_error_rate(self, rate: float) -> Dict[str, Any]:
        self.error_rate = min(1.0, max(0.0, float(rate)))
        incident = {
            "type": "ERROR_RATE_SPIKE",
            "value": f"{int(self.error_rate * 100)}%",
            "timestamp": time.time(),
            "description": f"Injected synthetic 500 error rate at {int(self.error_rate * 100)}%"
        }
        self.active_incidents.append(incident)
        logger.warning(f"[CHAOS] Error rate injected: {self.error_rate * 100}%")
        return incident

    def inject_memory_leak(self, mb: int) -> Dict[str, Any]:
        # Allocate uncollectible memory chunks
        bytes_to_alloc = int(mb) * 1024 * 1024
        chunk = bytearray(bytes_to_alloc)
        self.memory_buffer.append(chunk)
        total_mb = sum(len(c) for c in self.memory_buffer) / (1024 * 1024)
        incident = {
            "type": "MEMORY_LEAK",
            "value": f"+{mb}MB (total {total_mb:.1f}MB)",
            "timestamp": time.time(),
            "description": f"Allocated {mb}MB into persistent unmanaged buffer"
        }
        self.active_incidents.append(incident)
        logger.warning(f"[CHAOS] Memory leak injected: +{mb}MB, total leaked: {total_mb:.1f}MB")
        return incident

    def reset(self) -> Dict[str, Any]:
        self.latency_ms = 0.0
        self.error_rate = 0.0
        self.memory_buffer.clear()
        self.simulated_crash = False
        self.active_incidents.clear()
        logger.info("[CHAOS] All chaos parameters reset to normal baseline")
        return {"status": "healthy", "message": "All chaos parameters reset"}

    def get_status(self) -> Dict[str, Any]:
        total_leaked_mb = sum(len(c) for c in self.memory_buffer) / (1024 * 1024)
        return {
            "latency_ms": self.latency_ms,
            "error_rate": self.error_rate,
            "leaked_memory_mb": round(total_leaked_mb, 2),
            "is_degraded": (self.latency_ms > 0 or self.error_rate > 0 or total_leaked_mb > 100),
            "active_incidents": self.active_incidents[-5:]
        }

chaos_controller = ChaosController()
