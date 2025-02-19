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