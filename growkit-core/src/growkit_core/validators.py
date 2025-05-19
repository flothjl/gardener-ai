from math import dist
from typing import List, Optional, Tuple

from pydantic import BaseModel

from growkit_core.models import Bed, Garden, GardenTask, Planting


class GardenValidationException(Exception):
    def __init__(self, issues):
        self.issues = issues
        msg = "Garden validation failed:\n" + "\n".join(i.message for i in issues)
        super().__init__(msg)


def validate_spacing_conflicts(bed: Bed) -> List[Tuple[Planting, Planting]]:
    """
    Returns a list of (planting1, planting2) tuples that are too close together
    (based on max of their spacing values).
    """
    conflicts = []
    for i, p1 in enumerate(bed.plantings):
        for j, p2 in enumerate(bed.plantings):
            if i >= j:
                continue  # skip self or repeats
            spacing1 = p1.spacing or 0
            spacing2 = p2.spacing or 0
            min_distance = max(spacing1, spacing2)
            if dist(p1.position, p2.position) < min_distance:
                conflicts.append((p1, p2))
    return conflicts


def validate_bed_boundaries(bed: Bed) -> List[Planting]:
    """
    Returns plantings that are outside the bed's boundaries (width, length).
    Assumes bed is laid out starting at (0,0) and extends to (width, length).
    """
    issues = []
    width, length = bed.dimensions.width, bed.dimensions.length
    for p in bed.plantings:
        x, y = p.position
        if not (0 <= x <= width and 0 <= y <= length):
            issues.append(p)
    return issues


def validate_garden_spacing(garden: Garden) -> List[Tuple[str, Planting, Planting]]:
    """
    Checks all beds for spacing conflicts. Returns (bed name, planting1, planting2).
    """
    issues = []
    for bed in garden.beds:
        for p1, p2 in validate_spacing_conflicts(bed):
            issues.append((bed.name, p1, p2))
    return issues


def validate_task_dates(garden: Garden) -> List[GardenTask]:
    """
    Returns a list of tasks where the target_date is before the planting's planted_on
    or before the garden's created_at (if not related to a planting).
    """
    invalid_tasks = []
    plantings_by_id = {p.id: p for bed in garden.beds for p in bed.plantings}
    for task in garden.tasks:
        # Planting-specific tasks
        if task.related_planting_id:
            planting = plantings_by_id.get(task.related_planting_id)
            if (
                planting
                and planting.planted_on
                and task.target_date < planting.planted_on
            ):
                invalid_tasks.append(task)
        else:
            # General garden task
            if task.target_date < garden.created_at.date():
                invalid_tasks.append(task)
    return invalid_tasks


class GardenValidationIssue(BaseModel):
    type: str
    message: str
    bed_name: Optional[str] = None
    planting1_id: Optional[str] = None
    planting2_id: Optional[str] = None
    task_id: Optional[str] = None


def validate_garden(garden: Garden) -> List[GardenValidationIssue]:
    issues = []
    for bed in garden.beds:
        for p1, p2 in validate_spacing_conflicts(bed):
            issues.append(
                GardenValidationIssue(
                    type="spacing_conflict",
                    message=f"Plantings {p1.species} and {p2.species} are too close together in bed '{bed.name}'.",
                    bed_name=bed.name,
                    planting1_id=p1.id,
                    planting2_id=p2.id,
                )
            )
    for bed in garden.beds:
        for p in validate_bed_boundaries(bed):
            issues.append(
                GardenValidationIssue(
                    type="bed_boundary",
                    message=f"Planting {p.species} at position {p.position} is outside the boundaries of bed '{bed.name}'.",
                    bed_name=bed.name,
                    planting1_id=p.id,
                )
            )
    for task in validate_task_dates(garden):
        if task.related_planting_id:
            issues.append(
                GardenValidationIssue(
                    type="task_date",
                    message=f"Task '{task.title}' is scheduled before planting date.",
                    task_id=task.id,
                    planting1_id=task.related_planting_id,
                )
            )
        else:
            issues.append(
                GardenValidationIssue(
                    type="task_date",
                    message=f"Task '{task.title}' is scheduled before garden creation.",
                    task_id=task.id,
                )
            )
    return issues
