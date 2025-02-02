from pydantic import BaseModel, Field


class InputModel(BaseModel):
    """
    StarAtlas Warp Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    destination_x: int = Field(
        default=0,
        description="Warp to coordinate X",
    )

    destination_y: int = Field(
        default=0,
        description="Warp to coordinate Y",
    )


class OutputModel(BaseModel):
    """
    StarAtlas Warp Piece Output Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    destination_x: int = Field(
        description="Warped to X"
    )

    destination_y: int = Field(
        description="Warped to Y"
    )