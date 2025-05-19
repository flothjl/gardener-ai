from datetime import date, datetime, timezone

from growkit_core.models import (
    Bed,
    Dimensions,
    Garden,
    GardenTask,
    Planting,
    TaskStatus,
)
from growkit_core.validators import (
    validate_bed_boundaries,
    validate_garden_spacing,
    validate_spacing_conflicts,
    validate_task_dates,
)


def make_bed_with_plantings(plantings):
    return Bed(
        name="Test Bed",
        position=(0, 0),
        dimensions=Dimensions(width=1.0, length=1.0),
        plantings=plantings,
    )


def test_validate_spacing_conflicts_none():
    p1 = Planting(species="Lettuce", position=(0.1, 0.1), spacing=0.1)
    p2 = Planting(species="Carrot", position=(0.8, 0.8), spacing=0.1)
    bed = make_bed_with_plantings([p1, p2])
    conflicts = validate_spacing_conflicts(bed)
    assert conflicts == []


def test_validate_spacing_conflicts_detects_overlap():
    p1 = Planting(species="Lettuce", position=(0.1, 0.1), spacing=0.2)
    p2 = Planting(species="Carrot", position=(0.25, 0.15), spacing=0.2)
    bed = make_bed_with_plantings([p1, p2])
    conflicts = validate_spacing_conflicts(bed)
    assert len(conflicts) == 1
    assert (p1, p2) in conflicts or (p2, p1) in conflicts


def test_validate_bed_boundaries_none():
    p1 = Planting(species="Bean", position=(0.9, 0.8), spacing=0.1)
    bed = make_bed_with_plantings([p1])
    issues = validate_bed_boundaries(bed)
    assert issues == []


def test_validate_bed_boundaries_outside():
    p1 = Planting(species="Bean", position=(1.1, 0.5), spacing=0.1)
    p2 = Planting(species="Corn", position=(-0.2, 0.3), spacing=0.1)
    bed = make_bed_with_plantings([p1, p2])
    issues = validate_bed_boundaries(bed)
    assert p1 in issues
    assert p2 in issues


def test_validate_garden_spacing_combines_beds():
    p1 = Planting(species="A", position=(0.1, 0.1), spacing=0.2)
    p2 = Planting(species="B", position=(0.25, 0.15), spacing=0.2)
    b1 = make_bed_with_plantings([p1, p2])
    b2 = make_bed_with_plantings([])
    garden = Garden(name="Test", beds=[b1, b2])
    issues = validate_garden_spacing(garden)
    assert len(issues) == 1
    assert issues[0][0] == b1.name
    assert (p1, p2) == (issues[0][1], issues[0][2]) or (p2, p1) == (
        issues[0][1],
        issues[0][2],
    )


def test_validate_task_dates_ok():
    planting = Planting(
        species="Lettuce", position=(0.5, 0.5), spacing=0.2, planted_on=date(2025, 5, 1)
    )
    bed = make_bed_with_plantings([planting])
    garden = Garden(
        name="G",
        beds=[bed],
        created_at=datetime(2025, 4, 1, tzinfo=timezone.utc),
        tasks=[],
    )
    task = GardenTask(
        title="Thin seedlings",
        target_date=date(2025, 5, 3),
        related_planting_id=planting.id,
        status=TaskStatus.pending,
    )
    garden.tasks.append(task)
    invalid = validate_task_dates(garden)
    assert invalid == []


def test_validate_task_dates_invalid():
    planting = Planting(
        species="Lettuce",
        position=(0.5, 0.5),
        spacing=0.2,
        planted_on=date(2025, 5, 10),
    )
    bed = make_bed_with_plantings([planting])
    garden = Garden(
        name="G",
        beds=[bed],
        created_at=datetime(2025, 4, 1, tzinfo=timezone.utc),
        tasks=[],
    )
    task = GardenTask(
        title="Thin seedlings",
        target_date=date(2025, 5, 5),  # before planting planted_on
        related_planting_id=planting.id,
        status=TaskStatus.pending,
    )
    garden.tasks.append(task)
    invalid = validate_task_dates(garden)
    assert len(invalid) == 1
    assert invalid[0] == task


def test_validate_task_dates_invalid_general():
    garden = Garden(
        name="G",
        beds=[],
        created_at=datetime(2025, 5, 1, tzinfo=timezone.utc),
        tasks=[],
    )
    task = GardenTask(
        title="General Task",
        target_date=date(2025, 4, 20),  # before garden created
        status=TaskStatus.pending,
    )
    garden.tasks.append(task)
    invalid = validate_task_dates(garden)
    assert len(invalid) == 1
    assert invalid[0] == task
