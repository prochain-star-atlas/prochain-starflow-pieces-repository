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
    StarAtlas Unload All Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    destination_x: int = Field(
        default=0,
        description="Coordinate X target starbase",
    )

    destination_y: int = Field(
        default=0,
        description="Coordinate Y target starbase",
    )

    include_fuel: bool = Field(
        default=False,
        description="Fleet Name",
    )

    include_ammo: bool = Field(
        default=False,
        description="Fleet Name",
    )

    keep_one: bool = Field(
        default=False,
        description="Fleet Name",
    )
    
class OutputModel(BaseModel):
    """
    StarAtlas Unload All Piece Output Model
    """

    fleet_name: str = Field(
        description="Amount Resource loaded"
    )

    destination_x: int = Field(
        description="Load Cargo executed on X"
    )

    destination_y: int = Field(
        description="Load Cargo executed on Y"
    )
