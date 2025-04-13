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
        description="position_x",
    )

    position_y: int = Field(
        default=0,
        description="position_y",
    )

    destination_x: int = Field(
        default=0,
        description="destination_x",
    )

    destination_y: int = Field(
        default=0,
        description="destination_y",
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
        description="position_x",
    )

    position_y: int = Field(
        default=0,
        description="position_y",
    )

    destination_x: int = Field(
        default=0,
        description="destination_x",
    )

    destination_y: int = Field(
        default=0,
        description="destination_y",
    )

    distance_calculated: int = Field(
        default=0,
        description="distance_calculated",
    )

    subwarp_fuel_required: int = Field(
        default=0,
        description="subwarp_fuel_required",
    )

    subwarp_time_calculated: float = Field(
        default=0,
        description="subwarp_time_calculated",
    )

    subwarp_time_minutes_calculated: float = Field(
        default=0,
        description="subwarp_time_minutes_calculated",
    )

    warp_fuel_required: int = Field(
        default=0,
        description="warp_fuel_required",
    )

    warp_time_calculated: float = Field(
        default=0,
        description="warp_time_calculated",
    )

    warp_time_minutes_calculated: float = Field(
        default=0,
        description="warp_time_minutes_calculated",
    )

    warp_time_with_cooldown_calculated: float = Field(
        default=0,
        description="warp_time_with_cooldown_calculated",
    )

    warp_time_with_cooldown_minutes_calculated: float = Field(
        default=0,
        description="warp_time_with_cooldown_minutes_calculated",
    )

    
