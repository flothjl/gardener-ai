from datetime import date

from growkit_core.models import Bed, Coordinates, Dimensions, Garden, Plant


def test_create_minimal_garden():
    garden = Garden(name="Simple Garden", beds=[])
    assert garden.name == "Simple Garden"
    assert isinstance(garden.id, str)
    assert garden.location is None
    assert garden.beds == []


def test_garden_with_bed_and_plant():
    plant = Plant(
        species="Tomato",
        variety="Roma",
        planted_on=date(2025, 5, 1),
        expected_harvest=date(2025, 8, 1),
        notes="Needs support structure",
    )
    bed = Bed(
        name="Bed 1",
        position=(0.0, 0.0),
        dimensions=Dimensions(width=1.5, length=3.0),
        plants=[plant],
        soil_type="loam",
    )
    garden = Garden(
        name="Backyard",
        location=Coordinates(latitude=41.0, longitude=-96.0),
        beds=[bed],
    )
    assert garden.beds[0].plants[0].species == "Tomato"
    assert garden.location and garden.location.latitude == 41.0
