from datetime import date, datetime, timezone
from enum import Enum
from typing import List, Optional, Tuple
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "0.0.1"


class UnitLength(str, Enum):
    meters = "m"
    feet = "ft"
    inches = "in"


class Dimensions(BaseModel):
    width: float
    length: float
    depth: Optional[float] = None
    unit: UnitLength = UnitLength.meters


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class Plant(BaseModel):
    species: str
    variety: Optional[str] = None
    planted_on: Optional[date] = None
    expected_harvest: Optional[date] = None
    notes: Optional[str] = None


class Bed(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    position: Optional[Tuple[float, float]] = None  # x, y in meters
    dimensions: Dimensions
    plants: List[Plant] = Field(default=[])
    soil_type: Optional[str] = None


class Garden(BaseModel):
    model_config = ConfigDict(json_schema_extra={"schema_version": SCHEMA_VERSION})
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    location: Optional[Coordinates] = None
    beds: List[Bed] = Field(default=[])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
