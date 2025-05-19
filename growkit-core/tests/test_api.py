import pytest

from growkit_core.api import (
    AddBedParams,
    AddPlantingParams,
    AddTaskParams,
    CreateGardenParams,
    MoveBedParams,
    RemoveBedParams,
    RemovePlantingParams,
    UpdateBedDimensionsParams,
    UpdateGardenMetadataParams,
    add_bed,
    add_planting,
    add_task,
    create_garden,
    move_bed,
    remove_bed,
    remove_planting,
    update_bed_dimensions,
    update_garden_metadata,
)
from growkit_core.models import Coordinates, UnitLength
from growkit_core.validators import GardenValidationException, validate_garden


def test_create_garden_with_coords():
    garden = create_garden(
        CreateGardenParams(name="AI Garden", latitude=41.0, longitude=-96.0)
    )

    assert garden.name == "AI Garden"
    assert garden.location is not None
    assert garden.location.latitude == 41.0
    assert garden.beds == []


def test_add_bed_to_garden():
    garden = create_garden(CreateGardenParams(name="Test Garden"))
    params = AddBedParams(
        name="Bed A",
        position=(0, 0),
        width=1.5,
        length=2.0,
        unit=UnitLength.feet,
        soil_type="sandy",
    )
    garden = add_bed(garden, params)
    assert len(garden.beds) == 1
    bed = garden.beds[0]
    assert bed.name == "Bed A"
    assert bed.dimensions.width == 1.5
    assert bed.dimensions.unit == UnitLength.feet
    assert bed.soil_type == "sandy"


def test_add_planting_to_bed():
    garden = create_garden(CreateGardenParams(name="Planting Test Garden"))
    bed_params = AddBedParams(name="Bed X", width=1.0, length=1.0)
    garden = add_bed(garden, bed_params)
    bed_id = garden.beds[0].id

    planting_params = AddPlantingParams(
        bed_id=bed_id,
        species="Lettuce",
        variety="Romaine",
        position=(0.2, 0.3),
        spacing=0.15,
    )
    garden = add_planting(garden, planting_params)
    bed = garden.beds[0]
    assert len(bed.plantings) == 1
    assert bed.plantings[0].species == "Lettuce"
    assert bed.plantings[0].variety == "Romaine"
    assert bed.plantings[0].position == (0.2, 0.3)


def test_add_planting_spacing_conflict_raises():
    garden = create_garden(CreateGardenParams(name="Conflict Garden"))
    garden = add_bed(garden, AddBedParams(name="Bed Y", width=1.0, length=1.0))
    bed_id = garden.beds[0].id

    # Add the first planting
    garden = add_planting(
        garden,
        AddPlantingParams(
            bed_id=bed_id,
            species="Radish",
            position=(0.1, 0.1),
            spacing=0.2,
        ),
    )
    # Add the conflicting planting - should raise exception
    with pytest.raises(GardenValidationException):
        add_planting(
            garden,
            AddPlantingParams(
                bed_id=bed_id,
                species="Carrot",
                position=(0.15, 0.15),
                spacing=0.2,
            ),
        )


def test_add_planting_spacing_conflict_manual_validation():
    # This test shows how to bypass validation and check manually
    garden = create_garden(CreateGardenParams(name="Conflict Garden"))
    garden = add_bed(garden, AddBedParams(name="Bed Y", width=1.0, length=1.0))
    bed_id = garden.beds[0].id

    # Add both plantings with validation off
    garden = add_planting(
        garden,
        AddPlantingParams(
            bed_id=bed_id,
            species="Radish",
            position=(0.1, 0.1),
            spacing=0.2,
        ),
        validate=False,
    )
    garden = add_planting(
        garden,
        AddPlantingParams(
            bed_id=bed_id,
            species="Carrot",
            position=(0.15, 0.15),
            spacing=0.2,
        ),
        validate=False,
    )
    issues = validate_garden(garden)
    assert any(issue.type == "spacing_conflict" for issue in issues)


def test_move_bed():
    garden = create_garden(CreateGardenParams(name="Movable Garden"))
    bed = add_bed(garden, AddBedParams(name="Bed A", width=1.0, length=1.0)).beds[0]

    garden = move_bed(garden, MoveBedParams(bed_id=bed.id, new_position=(5.0, 10.0)))
    assert garden.beds[0].position == (5.0, 10.0)


def test_remove_bed():
    garden = create_garden(CreateGardenParams(name="Delete Bed Garden"))
    bed = add_bed(garden, AddBedParams(name="Temp Bed", width=1.0, length=1.0)).beds[0]

    garden = remove_bed(garden, RemoveBedParams(bed_id=bed.id))
    assert all(b.id != bed.id for b in garden.beds)


def test_remove_planting():
    garden = create_garden(CreateGardenParams(name="Remove Planting Garden"))
    bed = add_bed(garden, AddBedParams(name="Bed", width=1.0, length=1.0)).beds[0]
    bed_id = bed.id

    garden = add_planting(
        garden, AddPlantingParams(bed_id=bed_id, species="Kale", position=(0.1, 0.1))
    )
    garden = add_planting(
        garden, AddPlantingParams(bed_id=bed_id, species="Beet", position=(0.2, 0.2))
    )

    # Remove the first planting
    garden = remove_planting(
        garden, RemovePlantingParams(bed_id=bed_id, planting_index=0)
    )
    assert garden.beds[0].plantings[0].species == "Beet"
    assert len(garden.beds[0].plantings) == 1


def test_update_bed_dimensions():
    garden = create_garden(CreateGardenParams(name="Resize Garden"))
    bed = add_bed(garden, AddBedParams(name="Resizable", width=1.0, length=2.0)).beds[0]

    garden = update_bed_dimensions(
        garden,
        UpdateBedDimensionsParams(
            bed_id=bed.id, width=2.0, length=4.0, unit=UnitLength.feet
        ),
    )
    assert garden.beds[0].dimensions.width == 2.0
    assert garden.beds[0].dimensions.unit == UnitLength.feet


def test_update_garden_metadata():
    garden = create_garden(CreateGardenParams(name="Old Name"))
    garden = update_garden_metadata(
        garden,
        UpdateGardenMetadataParams(
            name="New Name", location=Coordinates(latitude=42.0, longitude=-95.0)
        ),
    )
    assert garden.name == "New Name"
    assert garden.location and garden.location.latitude == 42.0


def test_add_garden_task():
    from datetime import date

    garden = create_garden(CreateGardenParams(name="Test Tasks"))
    garden = add_task(
        garden,
        AddTaskParams(
            title="Mulch All Beds",
            target_date=date(2025, 5, 20),
            description="Apply mulch to conserve water.",
        ),
    )
    assert len(garden.tasks) == 1
    assert garden.tasks[0].title == "Mulch All Beds"
    assert garden.tasks[0].related_planting_id is None
