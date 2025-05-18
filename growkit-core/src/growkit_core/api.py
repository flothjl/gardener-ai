from datetime import date, datetime, timedelta, timezone
from typing import Annotated, Optional, Tuple
from uuid import uuid4

from pydantic import BaseModel, Field

from growkit_core.models import (
    Bed,
    Coordinates,
    Dimensions,
    Garden,
    GardenTask,
    Planting,
    TaskStatus,
    UnitLength,
)

NonEmptyStr = Annotated[str, Field(min_length=1)]
NonZeroPositiveFloat = Annotated[float, Field(gt=0)]


# ---------- Garden Metadata ----------


class UpdateGardenMetadataParams(BaseModel):
    name: Optional[NonEmptyStr] = None
    location: Optional[Coordinates] = None


def update_garden_metadata(
    garden: Garden, params: UpdateGardenMetadataParams
) -> Garden:
    if params.name:
        garden.name = params.name
    if params.location:
        garden.location = params.location
    return garden


# ---------- Bed Management ----------


class UpdateBedDimensionsParams(BaseModel):
    bed_id: NonEmptyStr
    width: NonZeroPositiveFloat
    length: NonZeroPositiveFloat
    depth: Optional[NonZeroPositiveFloat] = None
    unit: UnitLength = UnitLength.meters


def update_bed_dimensions(garden: Garden, params: UpdateBedDimensionsParams) -> Garden:
    for bed in garden.beds:
        if bed.id == params.bed_id:
            bed.dimensions = Dimensions(
                width=params.width,
                length=params.length,
                depth=params.depth,
                unit=params.unit,
            )
            return garden
    raise ValueError(f"No bed found with id '{params.bed_id}'")


class RemovePlantingParams(BaseModel):
    bed_id: NonEmptyStr
    planting_index: int  # You may want to allow removing by ID in the future


def remove_planting(garden: Garden, params: RemovePlantingParams) -> Garden:
    for bed in garden.beds:
        if bed.id == params.bed_id:
            if 0 <= params.planting_index < len(bed.plantings):
                del bed.plantings[params.planting_index]
                return garden
            raise IndexError("Invalid planting index")
    raise ValueError(f"No bed found with id '{params.bed_id}'")


class RemoveBedParams(BaseModel):
    bed_id: str


def remove_bed(garden: Garden, params: RemoveBedParams) -> Garden:
    garden.beds = [bed for bed in garden.beds if bed.id != params.bed_id]
    return garden


class MoveBedParams(BaseModel):
    bed_id: str
    new_position: Tuple[float, float]


def move_bed(garden: Garden, params: MoveBedParams) -> Garden:
    for bed in garden.beds:
        if bed.id == params.bed_id:
            bed.position = params.new_position
            return garden
    raise ValueError(f"No bed found with id '{params.bed_id}'")


class AddBedParams(BaseModel):
    name: NonEmptyStr
    position: Optional[Tuple[float, float]] = None
    width: NonZeroPositiveFloat
    length: NonZeroPositiveFloat
    depth: Optional[NonZeroPositiveFloat] = None
    unit: UnitLength = UnitLength.meters
    soil_type: Optional[NonEmptyStr] = None


def add_bed(garden: Garden, params: AddBedParams) -> Garden:
    new_bed = Bed(
        id=str(uuid4()),
        name=params.name,
        position=params.position,
        dimensions=Dimensions(
            width=params.width,
            length=params.length,
            depth=params.depth,
            unit=params.unit,
        ),
        soil_type=params.soil_type,
        plantings=[],
    )
    garden.beds.append(new_bed)
    return garden


# ---------- Planting Management ----------


class AddPlantingParams(BaseModel):
    bed_id: NonEmptyStr
    species: NonEmptyStr
    variety: Optional[NonEmptyStr] = None
    planted_on: Optional[date] = None
    expected_harvest: Optional[date] = None
    spacing: Optional[NonZeroPositiveFloat] = None
    position: Tuple[float, float]
    notes: Optional[NonEmptyStr] = None


def add_planting(garden: Garden, params: AddPlantingParams) -> Garden:
    """
    Adds a planting to the specified bed. If spacing is not provided,
    it is looked up from the crop definition if available.
    If a crop definition exists and includes a timeline,
    corresponding tasks are generated and added to the garden.
    """
    for bed in garden.beds:
        if bed.id == params.bed_id:
            spacing = params.spacing

            new_planting = Planting(
                id=str(uuid4()),
                species=params.species,
                variety=params.variety,
                planted_on=params.planted_on,
                expected_harvest=params.expected_harvest,
                spacing=spacing,
                position=params.position,
                notes=params.notes,
            )
            bed.plantings.append(new_planting)

            return garden

    raise ValueError(f"No bed found with id '{params.bed_id}'")


# ---------- Garden Creation ----------


class CreateGardenParams(BaseModel):
    name: NonEmptyStr
    latitude: Optional[float] = None
    longitude: Optional[float] = None


def create_garden(params: CreateGardenParams) -> Garden:
    location = None
    if params.latitude is not None and params.longitude is not None:
        location = Coordinates(latitude=params.latitude, longitude=params.longitude)

    return Garden(
        name=params.name,
        location=location,
        beds=[],
        tasks=[],
        created_at=datetime.now(timezone.utc),
    )


class AddTaskParams(BaseModel):
    title: NonEmptyStr
    target_date: date
    description: Optional[str] = None
    related_planting_id: Optional[str] = None
    related_bed_id: Optional[str] = None


def add_task(garden: Garden, params: AddTaskParams) -> Garden:
    task = GardenTask(
        id=str(uuid4()),
        title=params.title,
        description=params.description,
        target_date=params.target_date,
        status=TaskStatus.pending,
        related_planting_id=params.related_planting_id,
        related_bed_id=params.related_bed_id,
    )
    garden.tasks.append(task)
    return garden


def add_planting_task(
    garden: Garden,
    planting_id: str,
    title: str,
    target_date: date,
    description: Optional[str] = None,
) -> Garden:
    bed_id = None
    for bed in garden.beds:
        if any(p.id == planting_id for p in bed.plantings):
            bed_id = bed.id
            break
    return add_task(
        garden,
        AddTaskParams(
            title=title,
            target_date=target_date,
            description=description,
            related_planting_id=planting_id,
            related_bed_id=bed_id,
        ),
    )
