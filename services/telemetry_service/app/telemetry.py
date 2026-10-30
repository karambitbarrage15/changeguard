"""
Telemetry Models & Ingestion Buffer for Connected Vehicles.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import time
import random

class Location(BaseModel):
    latitude: float
    longitude: float
    altitude_m: Optional[float] = 120.5

class VehicleTelemetry(BaseModel):
    vin: str = Field(..., description="Vehicle Identification Number")
    fleet_id: str = Field(default="fleet-alpha")
    speed_kmh: float = Field(ge=0.0, le=300.0)
    battery_pct: float = Field(ge=0.0, le=100.0)
    motor_temp_c: float = Field(default=65.0)
    tire_pressure_psi: float = Field(default=33.5)
    location: Location
    firmware_version: str = Field(default="v2.4.1-rc3")
    timestamp: float = Field(default_factory=time.time)

class TelemetryStore:
    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self.records: List[Dict[str, Any]] = []
        self.vehicles: Dict[str, Dict[str, Any]] = {}

    def ingest(self, telemetry: VehicleTelemetry) -> Dict[str, Any]:
        data = telemetry.model_dump()
        self.records.append(data)
        if len(self.records) > self.max_records:
            self.records.pop(0)
        self.vehicles[telemetry.vin] = data
        return {"status": "ingested", "vin": telemetry.vin, "ts": data["timestamp"]}

    def get_latest(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.records[-limit:]

    def get_vehicle_count(self) -> int:
        return len(self.vehicles)

    def generate_sample(self, vin_idx: int = 1) -> VehicleTelemetry:
        vins = ["VIN-TESLA-9921", "VIN-RIVIAN-4402", "VIN-POLSTAR-1109", "VIN-LUCID-8831", "VIN-VOLVO-5510"]
        chosen_vin = vins[vin_idx % len(vins)]
        return VehicleTelemetry(
            vin=chosen_vin,
            fleet_id="fleet-california-01",
            speed_kmh=round(random.uniform(40.0, 110.0), 1),
            battery_pct=round(random.uniform(25.0, 95.0), 1),
            motor_temp_c=round(random.uniform(55.0, 85.0), 1),
            tire_pressure_psi=round(random.uniform(32.0, 35.0), 1),
            location=Location(
                latitude=37.7749 + random.uniform(-0.05, 0.05),
                longitude=-122.4194 + random.uniform(-0.05, 0.05)
            ),
            firmware_version="v2.4.1-rc3"
        )

telemetry_store = TelemetryStore()
