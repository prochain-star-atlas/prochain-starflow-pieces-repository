from enum import Enum
from pydantic import BaseModel, Field

class InputModel(BaseModel):
    """
    StarAtlas Mining Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    position_x: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    position_y: int = Field(
        default=0,
        description="Number of seconds to sleep",
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
    StarAtlas Mining Piece Output Model
    """
    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    position_x: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    position_y: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    destination_x: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    destination_y: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    distance_calculated: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    subwarp_fuel_required: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    subwarp_time_calculated: float = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    subwarp_time_minutes_calculated: float = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    warp_fuel_required: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    warp_time_calculated: float = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    warp_time_minutes_calculated: float = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    warp_time_with_cooldown_calculated: float = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    warp_time_with_cooldown_minutes_calculated: float = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    
