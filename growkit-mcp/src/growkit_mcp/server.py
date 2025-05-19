from growkit_core.api import (
    AddBedParams,
    AddPlantingParams,
    CreateGardenParams,
    MoveBedParams,
    RemoveBedParams,
    RemovePlantingParams,
    UpdateBedDimensionsParams,
    UpdateGardenMetadataParams,
    add_bed,
    add_planting,
    create_garden,
    move_bed,
    remove_bed,
    remove_planting,
    update_bed_dimensions,
    update_garden_metadata,
)
from growkit_core.models import Garden
from growkit_core.validators import GardenValidationException
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_REQUEST, ErrorData

INSTRUCTIONS = """
You are a garden planning assistant. You help users construct and modify digital garden plans.
All changes must be reflected in the garden structure, and should be consistent and explainable.
Units, positions, and names must always be honored. Be explicit and safe.
"""

mcp = FastMCP("Growkit Garden Agent", INSTRUCTIONS)


def _validation_error(e: GardenValidationException):
    # Return all error messages as a single string or list as you see fit
    return McpError(
        ErrorData(
            message="\n".join([issue.message for issue in e.issues]),
            code=INVALID_REQUEST,
        )
    )


@mcp.tool("CreateGarden")
def mcp_create_garden(params: CreateGardenParams) -> Garden:
    """
    Creates a new garden with the given name. Optionally, provide latitude and longitude to geolocate the garden.
    If coordinates are not provided, the garden will be treated as an abstract or simulated space.
    """
    return create_garden(
        CreateGardenParams(
            name=params.name, latitude=params.latitude, longitude=params.longitude
        )
    )


@mcp.tool("AddBed")
def mcp_add_bed(garden: Garden, params: AddBedParams) -> Garden:
    """
    Adds a new bed to the specified garden.
    Validates that bed name is not empty and dimensions are positive.
    """
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
    """
    Adds a planting to a specified bed in the garden.
    Requires the `bed_id` of the target bed and the plant's species name.
    Variety, notes, and planting/harvest dates can be included optionally.
    Validates that the specified bed exists and species name is provided.
    """
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


@mcp.tool("MoveBed")
def mcp_move_bed(garden: Garden, params: MoveBedParams) -> Garden:
    """
    Moves a bed to a new (x, y) position relative to the garden origin.
    Requires the `bed_id` and the new position as a tuple of floats.
    Validates that the bed exists.
    """
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
    """
    Removes a bed from the garden by its `bed_id`.
    If no bed is found, raises an error.
    """
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
    """
    Removes a planting from the given bed by its index in the planting list.
    Requires both `bed_id` and the planting's index in that bed's planting list.
    Validates that both the bed and index exist.
    """
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
    """
    Updates the dimensions (width, length, depth, unit) of a specified bed.
    Ensures the bed exists and that width/length are positive values.
    """
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
    """
    Updates garden-level metadata such as name or geolocation.
    All fields are optional. If no changes are provided, the garden is returned unchanged.
    """
    if not params.name and not params.location:
        raise McpError(
            ErrorData(
                message="At least one of 'name' or 'location' must be provided.",
                code=INVALID_REQUEST,
            )
        )
    return update_garden_metadata(garden, params)


@mcp.resource(
    uri="json://schema",
    description="get json schema for the gardener-ai platform.",
)
def get_json_schema():
    return Garden.model_json_schema()
