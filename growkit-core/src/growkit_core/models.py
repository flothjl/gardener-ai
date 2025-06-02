from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "0.0.2"


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


class Planting(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    species: str
    variety: Optional[str] = None
    planted_on: Optional[date] = None
    expected_harvest: Optional[date] = None
    position: Tuple[float, float]  # x, y coordinates within the bed
    spacing: Optional[float] = None  # in same unit as bed dimensions
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    skipped = "skipped"


class GardenTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: Optional[str] = None
    target_date: date
    completed_on: Optional[date] = None
    status: TaskStatus = TaskStatus.pending
    related_planting_id: Optional[str] = None
    related_bed_id: Optional[str] = None


class Bed(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    position: Optional[Tuple[float, float]] = None  # x, y in meters
    dimensions: Dimensions
    soil_type: Optional[str] = None
    plantings: List[Planting] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AgentCommentary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    comment: str


class Garden(BaseModel):
    model_config = ConfigDict(json_schema_extra={"schema_version": SCHEMA_VERSION})
    schema_version: str = SCHEMA_VERSION
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    location: Optional[Coordinates] = None
    beds: List[Bed] = Field(default_factory=list)
    tasks: List[GardenTask] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    average_last_frost: Optional[date] = None
    average_first_frost: Optional[date] = None
    agent_comments: List[AgentCommentary] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
