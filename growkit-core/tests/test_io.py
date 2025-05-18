import json
import tempfile
from datetime import date
from pathlib import Path

from growkit_core.io import load_garden, save_garden
from growkit_core.models import Bed, Dimensions, Garden, Planting


def make_sample_garden() -> Garden:
    planting = Planting(
        species="Carrot",
        variety="Nantes",
        planted_on=date(2025, 4, 1),
        expected_harvest=date(2025, 6, 1),
        position=(0.1, 0.1),
        spacing=0.05,
    )
    bed = Bed(
        name="Root Bed",
        position=(1.0, 2.0),
        dimensions=Dimensions(width=1.0, length=2.0),
        plantings=[planting],
    )
    return Garden(name="My Garden", beds=[bed])


def test_garden_serialization_roundtrip():
    garden = make_sample_garden()

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "garden.json"
        save_garden(garden, path)

        loaded = load_garden(path)
        assert loaded.name == garden.name
        assert loaded.beds[0].plantings[0].species == "Carrot"
        assert loaded.beds[0].dimensions.width == 1.0


def test_json_is_valid_json():
    garden = make_sample_garden()

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "garden.json"
        save_garden(garden, path)

        with open(path, "r") as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert data["name"] == "My Garden"
