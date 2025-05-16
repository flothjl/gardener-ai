from pathlib import Path

from growkit_core.models import Garden


def load_garden(path: Path) -> Garden:
    with open(path, "r", encoding="utf-8") as f:
        return Garden.model_validate_json(f.read())


def save_garden(garden: Garden, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(garden.model_dump_json(indent=2))
