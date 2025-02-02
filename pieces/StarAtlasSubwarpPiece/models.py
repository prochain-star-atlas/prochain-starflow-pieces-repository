from pydantic import BaseModel, Field


class InputModel(BaseModel):
    """
    StarAtlas Subwarp Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    destination_x: int = Field(
        default=0,
        description="Subwarp to coordinate X",
    )

    destination_y: int = Field(
        default=0,
        description="Subwarp to coordinate Y",
    )


class OutputModel(BaseModel):
    """
    StarAtlas Subwarp Piece Output Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    destination_x: int = Field(
        description="Subwarped to X"
    )

    destination_y: int = Field(
        description="Subwarped to Y"
    )