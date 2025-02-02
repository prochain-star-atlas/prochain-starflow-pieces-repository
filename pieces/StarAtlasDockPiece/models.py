from pydantic import BaseModel, Field


class InputModel(BaseModel):
    """
    StarAtlas Dock Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    destination_x: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    destination_y: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )


class OutputModel(BaseModel):
    """
    StarAtlas Dock Piece Output Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    destination_x: int = Field(
        description="Dock executed on X"
    )

    destination_y: int = Field(
        description="Dock executed on Y"
    )
