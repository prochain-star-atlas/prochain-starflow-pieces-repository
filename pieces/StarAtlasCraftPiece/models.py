from pydantic import BaseModel, Field


class InputModel(BaseModel):
    """
    StarAtlas Craft Piece Input Model
    """

    sleep_time: float = Field(
        default=1,
        description="Number of seconds to sleep",
    )


class OutputModel(BaseModel):
    """
    StarAtlas Craft Piece Input Model
    """
    message: str = Field(
        description="Sleep piece executed"
    )
