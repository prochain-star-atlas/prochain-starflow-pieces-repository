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
    StarAtlas Load Cargo Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    resource_mint: str = Field(
        default="",
        description="Resource to Load Cargo",
    )

    amount: int = Field(
        default="",
        description="Amount of Resource",
    )

    destination_x: int = Field(
        default=0,
        description="Coordinate X target starbase",
    )

    destination_y: int = Field(
        default=0,
        description="Coordinate Y target starbase",
    )


class OutputModel(BaseModel):
    """
    StarAtlas Load Cargo Piece Output Model
    """

    resource_mint_loaded: int = Field(
        description="Amount Resource loaded"
    )

    amount_loaded: int = Field(
        description="Amount Resource loaded"
    )

    destination_x: int = Field(
        description="Load Cargo executed on X"
    )

    destination_y: int = Field(
        description="Load Cargo executed on Y"
    )
