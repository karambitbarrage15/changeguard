"""
Prometheus metrics collector for Connected-Vehicle Telemetry Service.
"""
from prometheus_client import Counter, Gauge, Summary, make_asgi_app

REQUESTS_TOTAL = Counter(
    "changeguard_requests_total",
    "Total incoming telemetry API requests",
    ["endpoint", "status", "method"]
)

REQUEST_LATENCY = Summary(
    "changeguard_request_latency_seconds",
    "Request processing latency in seconds",
    ["endpoint"]
)

ACTIVE_VEHICLES = Gauge(
    "changeguard_active_vehicles",
    "Number of active reporting connected vehicles"
)

BATTERY_HEALTH = Gauge(
    "changeguard_battery_health_percentage",
    "Average vehicle battery state of charge (SoC)",
    ["fleet_id"]
)

MEMORY_USAGE = Gauge(
    "changeguard_memory_usage_bytes",
    "Current memory usage of telemetry service in bytes"
)

ERRORS_TOTAL = Counter(
    "changeguard_errors_total",
    "Total internal errors encountered in telemetry ingestion",
    ["error_type"]
)

metrics_app = make_asgi_app()
