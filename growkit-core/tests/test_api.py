from growkit_core.api import (
    AddBedParams,
    AddPlantParams,
    CreateGardenParams,
    MoveBedParams,
    RemoveBedParams,
    RemovePlantParams,
    UpdateBedDimensionsParams,
    UpdateGardenMetadataParams,
    add_bed,
    add_plant,
    create_garden,
    move_bed,
    remove_bed,
    remove_plant,
    update_bed_dimensions,
    update_garden_metadata,
)
from growkit_core.models import Coordinates, UnitLength


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


def test_add_plant_to_bed():
    garden = create_garden(CreateGardenParams(name="Plant Test Garden"))
    bed_params = AddBedParams(name="Bed X", width=1.0, length=1.0)
    garden = add_bed(garden, bed_params)
    bed_id = garden.beds[0].id

    plant_params = AddPlantParams(bed_id=bed_id, species="Lettuce", variety="Romaine")
    garden = add_plant(garden, plant_params)

    bed = garden.beds[0]
    assert len(bed.plants) == 1
    assert bed.plants[0].species == "Lettuce"
    assert bed.plants[0].variety == "Romaine"


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


def test_remove_plant():
    garden = create_garden(CreateGardenParams(name="Remove Plant Garden"))
    bed = add_bed(garden, AddBedParams(name="Bed", width=1.0, length=1.0)).beds[0]
    bed_id = bed.id
    garden = add_plant(garden, AddPlantParams(bed_id=bed_id, species="Kale"))
    garden = add_plant(garden, AddPlantParams(bed_id=bed_id, species="Beet"))

    garden = remove_plant(garden, RemovePlantParams(bed_id=bed_id, plant_index=0))
    assert garden.beds[0].plants[0].species == "Beet"
    assert len(garden.beds[0].plants) == 1


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
