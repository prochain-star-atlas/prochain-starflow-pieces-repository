from enum import Enum
from pydantic import BaseModel, Field
from decimal import *

class InputModel(BaseModel):
    """
    StarAtlas Mining Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

class OutputModel(BaseModel):
    """
    StarAtlas Mining Piece Output Model
    """
    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    transport_mode: str = Field(
        description="Transport Mode"
    )

    end_time: Decimal = Field(
        description="end_time"
    )

    end_time_remaining: Decimal = Field(
        description="end_time_remaining"
    )

    end_time_remaining_in_minutes: Decimal = Field(
        description="end_time_remaining_in_minutes"
    )

    from_sector_x: int = Field(
        description="from_sector_x"
    )

    from_sector_y: int = Field(
        description="from_sector_y"
    )

    to_sector_x: int = Field(
        description="to_sector_x"
    )

    to_sector_y: int = Field(
        description="to_sector_y"
    )

    
