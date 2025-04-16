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
    StarAtlas Mining Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    resource_mint: str = Field(
        default="",
        description="Resource to mine",
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
    StarAtlas Mining Piece Output Model
    """
    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    resource_mint_mined: str = Field(
        description="Resource Mint Mined"
    )

    resource_amount_mined: int = Field(
        description="Amount Resource Mined"
    )

    
