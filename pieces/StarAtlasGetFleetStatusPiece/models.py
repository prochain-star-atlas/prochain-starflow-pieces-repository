from enum import Enum
from pydantic import BaseModel, Field


class FleetStatusEnum(str, Enum):
    StarbaseLoadingBay = "StarbaseLoadingBay"
    ReadyToExitWarp = "ReadyToExitWarp"
    MineAsteroid = "MineAsteroid"
    MoveWarp = "MoveWarp"
    MoveSubwarp = "MoveSubwarp"
    Respawn = "Respawn"
    StarbaseUpgrade = "StarbaseUpgrade"
    Idle = "Idle"

class InputModel(BaseModel):
    """
    StarAtlas Dock Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )


class OutputModel(BaseModel):
    """
    StarAtlas Dock Piece Output Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    fleet_status: FleetStatusEnum = Field(
        description="Fleet Status"
    )
