import base64
import json
import os
import webbrowser
import zlib
from typing import List, Tuple
from urllib.parse import quote

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
from growkit_core.models import Garden
from growkit_core.validators import GardenValidationException, validate_garden
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_REQUEST, ErrorData
from pydantic import BaseModel

INSTRUCTIONS = """
You are a garden planning assistant. You help users construct and modify digital garden plans.
All changes must be reflected in the garden structure, and should be consistent and explainable.
Units, positions, and names must always be honored. Be explicit and safe.
"""

mcp = FastMCP("Growkit Garden Agent", INSTRUCTIONS)


def _validation_error(e: GardenValidationException):
    return McpError(
        ErrorData(
            message="\n".join([issue.message for issue in e.issues]),
            code=INVALID_REQUEST,
            data=[issue.dict() for issue in e.issues],  # Optional: full detail
        )
    )


@mcp.tool("CreateGarden")
def mcp_create_garden(params: CreateGardenParams) -> Garden:
    return create_garden(params)


@mcp.tool("AddBed")
def mcp_add_bed(garden: Garden, params: AddBedParams) -> Garden:
    if not params.name.strip():
        raise McpError(
            ErrorData(message="Bed name must not be empty.", code=INVALID_REQUEST)
        )
    if params.width <= 0 or params.length <= 0:
        raise McpError(
            ErrorData(
                message="Bed width and length must be greater than zero.",
                code=INVALID_REQUEST,
            )
        )
    try:
        return add_bed(garden, params, validate=True)
    except GardenValidationException as e:
        raise _validation_error(e)


@mcp.tool("AddPlanting")
def mcp_add_planting(garden: Garden, params: AddPlantingParams) -> Garden:
    if not params.species.strip():
        raise McpError(
            ErrorData(
                message="Plant species must not be empty.",
                code=INVALID_REQUEST,
            )
        )
    if not any(bed.id == params.bed_id for bed in garden.beds):
        raise McpError(
            ErrorData(
                message=f"No bed with id '{params.bed_id}' exists in the garden.",
                code=INVALID_REQUEST,
            )
        )
    try:
        return add_planting(garden, params, validate=True)
    except GardenValidationException as e:
        raise _validation_error(e)


@mcp.tool("AddTask")
def mcp_add_task(garden: Garden, params: AddTaskParams) -> Garden:
    return add_task(garden, params)


@mcp.tool("MoveBed")
def mcp_move_bed(garden: Garden, params: MoveBedParams) -> Garden:
    if not any(b.id == params.bed_id for b in garden.beds):
        raise McpError(
            ErrorData(
                message=f"No bed with id '{params.bed_id}' exists.",
                code=INVALID_REQUEST,
            )
        )
    try:
        return move_bed(garden, params, validate=True)
    except GardenValidationException as e:
        raise _validation_error(e)


@mcp.tool("RemoveBed")
def mcp_remove_bed(garden: Garden, params: RemoveBedParams) -> Garden:
    if not any(b.id == params.bed_id for b in garden.beds):
        raise McpError(
            ErrorData(
                message=f"No bed with id '{params.bed_id}' found.",
                code=INVALID_REQUEST,
            )
        )
    try:
        return remove_bed(garden, params, validate=True)
    except GardenValidationException as e:
        raise _validation_error(e)


@mcp.tool("RemovePlanting")
def mcp_remove_planting(garden: Garden, params: RemovePlantingParams) -> Garden:
    bed = next((b for b in garden.beds if b.id == params.bed_id), None)
    if not bed:
        raise McpError(
            ErrorData(
                message=f"Bed with id '{params.bed_id}' not found.",
                code=INVALID_REQUEST,
            )
        )
    if not (0 <= params.planting_index < len(bed.plantings)):
        raise McpError(
            ErrorData(
                message=f"Planting index {params.planting_index} is out of bounds for bed '{params.bed_id}'.",
                code=INVALID_REQUEST,
            )
        )
    try:
        return remove_planting(garden, params, validate=True)
    except GardenValidationException as e:
        raise _validation_error(e)


@mcp.tool("UpdateBedDimensions")
def mcp_update_bed_dimensions(
    garden: Garden, params: UpdateBedDimensionsParams
) -> Garden:
    if params.width <= 0 or params.length <= 0:
        raise McpError(
            ErrorData(
                message="Width and length must be greater than zero.",
                code=INVALID_REQUEST,
            )
        )
    if not any(b.id == params.bed_id for b in garden.beds):
        raise McpError(
            ErrorData(
                message=f"Bed with id '{params.bed_id}' not found.",
                code=INVALID_REQUEST,
            )
        )
    try:
        return update_bed_dimensions(garden, params, validate=True)
    except GardenValidationException as e:
        raise _validation_error(e)


@mcp.tool("UpdateGardenMetadata")
def mcp_update_garden_metadata(
    garden: Garden, params: UpdateGardenMetadataParams
) -> Garden:
    if not params.name and not params.location:
        raise McpError(
            ErrorData(
                message="At least one of 'name' or 'location' must be provided.",
                code=INVALID_REQUEST,
            )
        )
    return update_garden_metadata(garden, params)


class AddBedsParams(BaseModel):
    beds: List[AddBedParams]


@mcp.tool("AddBeds")
def mcp_add_beds(garden: Garden, params: AddBedsParams) -> Garden:
    """
    Adds multiple beds to the garden. All beds are validated at once.
    If any addition fails, the operation halts and errors are returned.
    """
    try:
        for bed_params in params.beds:
            garden = add_bed(garden, bed_params, validate=False)
        issues = validate_garden(garden)
        if issues:
            raise GardenValidationException(issues)
        return garden
    except GardenValidationException as e:
        raise _validation_error(e)
    except ValueError as e:
        raise McpError(ErrorData(message=str(e), code=INVALID_REQUEST))


class AddPlantingsParams(BaseModel):
    plantings: List[AddPlantingParams]


@mcp.tool("BulkAddPlantings")
def mcp_add_plantings(garden: Garden, params: AddPlantingsParams) -> Garden:
    """
    Adds multiple plantings to the garden (possibly different beds).
    Validates all at once. If any error occurs, no partial success is promised.
    """
    try:
        for planting_params in params.plantings:
            garden = add_planting(garden, planting_params, validate=False)
        issues = validate_garden(garden)
        if issues:
            raise GardenValidationException(issues)
        return garden
    except GardenValidationException as e:
        raise _validation_error(e)
    except ValueError as e:
        raise McpError(ErrorData(message=str(e), code=INVALID_REQUEST))


@mcp.tool("ValidateGarden")
def mcp_validate_garden(garden: Garden):
    """
    Validates the current garden state. Returns a list of validation issues, if any.
    """
    issues = validate_garden(garden)
    return [issue.model_dump() for issue in issues]


class RemovePlantingsParams(BaseModel):
    removals: List[Tuple[str, int]]  # List of (bed_id, planting_index)


@mcp.tool("RemovePlantings")
def mcp_remove_plantings(garden: Garden, params: RemovePlantingsParams) -> Garden:
    try:
        # Remove in reverse index order for each bed, so indices don't shift
        sorted_removals = sorted(params.removals, key=lambda x: (x[0], -x[1]))
        for bed_id, idx in sorted_removals:
            garden = remove_planting(
                garden,
                RemovePlantingParams(bed_id=bed_id, planting_index=idx),
                validate=False,
            )
        # Final validation
        issues = validate_garden(garden)
        if issues:
            raise GardenValidationException(issues)
        return garden
    except GardenValidationException as e:
        raise _validation_error(e)
    except ValueError as e:
        # Bed or index error from core API
        raise McpError(
            ErrorData(
                message=str(e),
                code=INVALID_REQUEST,
            )
        )


class RemoveBedsParams(BaseModel):
    bed_ids: List[str]


@mcp.tool("RemoveBeds")
def mcp_remove_beds(garden: Garden, params: RemoveBedsParams) -> Garden:
    """
    Removes multiple beds from the garden by ID. Validates at the end.
    """
    try:
        for bed_id in params.bed_ids:
            garden = remove_bed(garden, RemoveBedParams(bed_id=bed_id), validate=False)
        issues = validate_garden(garden)
        if issues:
            raise GardenValidationException(issues)
        return garden
    except GardenValidationException as e:
        raise _validation_error(e)
    except ValueError as e:
        raise McpError(ErrorData(message=str(e), code=INVALID_REQUEST))


class AddTasksParams(BaseModel):
    tasks: List[AddTaskParams]


@mcp.tool("AddTasks")
def mcp_add_tasks(garden: Garden, params: AddTasksParams) -> Garden:
    """
    Adds multiple tasks to the garden at once. Validates at the end.
    """
    try:
        for task_params in params.tasks:
            garden = add_task(garden, task_params)
        issues = validate_garden(garden)
        if issues:
            raise GardenValidationException(issues)
        return garden
    except GardenValidationException as e:
        raise _validation_error(e)
    except ValueError as e:
        raise McpError(ErrorData(message=str(e), code=INVALID_REQUEST))


@mcp.resource(
    uri="json://garden-schema",
    description="get json schema for gardens.",
)
def get_json_schema_garden():
    return Garden.model_json_schema()


@mcp.tool("ViewGarden")
def view_garden(garden: Garden) -> str:
    """
    Open a visualization for the garden in the user's default browser.
    Does not return the URL to the LLM, just true/false for success.
    """
    try:
        URL = os.environ["VIEWER_URL"]
    except KeyError:
        raise McpError(
            ErrorData(
                message="VIEWER_URL must be set as an environment variable",
                code=INVALID_REQUEST,
            )
        )
    garden_json = json.dumps(garden.model_dump(mode="json"), separators=(",", ":"))
    compressed = zlib.compress(garden_json.encode("utf-8"), level=9)
    b64 = base64.urlsafe_b64encode(compressed).decode("ascii")
    url = f"{URL}?data={quote(b64)}"
    try:
        webbrowser.open_new_tab(url)
        return "URL has been successfully opened!"
    except Exception as e:
        raise McpError(
            ErrorData(
                message=f"{e}",
                code=INVALID_REQUEST,
            )
        )
