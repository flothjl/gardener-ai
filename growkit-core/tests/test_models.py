from datetime import date

from growkit_core.models import (
    Bed,
    Coordinates,
    Dimensions,
    Garden,
    GardenTask,
    Planting,
    TaskStatus,
)


def test_create_minimal_garden():
    garden = Garden(name="Simple Garden", beds=[], tasks=[])
    assert garden.name == "Simple Garden"
    assert isinstance(garden.id, str)
    assert garden.location is None
    assert garden.beds == []
    assert garden.tasks == []


def test_garden_with_bed_and_planting():
    planting = Planting(
        species="Tomato",
        variety="Roma",
        planted_on=date(2025, 5, 1),
        expected_harvest=date(2025, 8, 1),
        position=(0.5, 0.5),
        spacing=0.3,
        notes="Needs support structure",
    )
    bed = Bed(
        name="Bed 1",
        position=(0.0, 0.0),
        dimensions=Dimensions(width=1.5, length=3.0),
        soil_type="loam",
        plantings=[planting],
    )
    garden = Garden(
        name="Backyard",
        location=Coordinates(latitude=41.0, longitude=-96.0),
        beds=[bed],
        tasks=[],
    )
    assert garden.beds[0].plantings[0].species == "Tomato"
    assert garden.location and garden.location.latitude == 41.0


def test_garden_with_task():
    task = GardenTask(
        title="Water tomatoes",
        description="Ensure deep watering in the morning.",
        target_date=date(2025, 5, 5),
        status=TaskStatus.pending,
    )
    garden = Garden(name="Task Garden", beds=[], tasks=[task])
    assert garden.tasks[0].title == "Water tomatoes"
    assert garden.tasks[0].status == TaskStatus.pending
