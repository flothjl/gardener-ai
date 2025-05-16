from datetime import date, datetime, timezone
from typing import Annotated, Optional, Tuple
from uuid import uuid4

from pydantic import BaseModel, Field

from growkit_core.models import Bed, Coordinates, Dimensions, Garden, Plant, UnitLength

NonEmptyStr = Annotated[str, Field(min_length=1)]
NonZeroPositiveFloat = Annotated[float, Field(gt=0)]


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


class RemovePlantParams(BaseModel):
    bed_id: NonEmptyStr
    plant_index: int


def remove_plant(garden: Garden, params: RemovePlantParams) -> Garden:
    for bed in garden.beds:
        if bed.id == params.bed_id:
            if 0 <= params.plant_index < len(bed.plants):
                del bed.plants[params.plant_index]
                return garden
            raise IndexError("Invalid plant index")
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
        plants=[],
    )
    garden.beds.append(new_bed)
    return garden


class AddPlantParams(BaseModel):
    bed_id: NonEmptyStr
    species: NonEmptyStr
    variety: Optional[NonEmptyStr] = None
    planted_on: Optional[date] = None
    expected_harvest: Optional[date] = None
    notes: Optional[NonEmptyStr] = None


def add_plant(garden: Garden, params: AddPlantParams) -> Garden:
    for bed in garden.beds:
        if bed.id == params.bed_id:
            new_plant = Plant(
                species=params.species,
                variety=params.variety,
                planted_on=params.planted_on,
                expected_harvest=params.expected_harvest,
                notes=params.notes,
            )
            bed.plants.append(new_plant)
            return garden

    raise ValueError(f"No bed found with id '{params.bed_id}'")


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
        created_at=datetime.now(timezone.utc),
    )
