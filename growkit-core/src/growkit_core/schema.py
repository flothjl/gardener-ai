import json
from pathlib import Path

from growkit_core.models import Garden


def get_garden_schema() -> dict:
    return Garden.model_json_schema()


def save_garden_schema(path: Path) -> None:
    schema = get_garden_schema()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
