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

    resource_mint: str = Field(
        default="",
        description="Resource to mine",
    )

    starbase_x: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    starbase_y: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    planet_x: int = Field(
        default=0,
        description="Number of seconds to sleep",
    )

    planet_y: int = Field(
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

    resource_mint_mined: str = Field(
        description="Resource Mint Mined"
    )

    mining_duration: float = Field(
        description="Amount Resource Mined"
    )

    mining_duration_in_minutes: float = Field(
        description="Amount Resource Mined"
    )

    amount_mined: int = Field(
        description="Amount Resource Mined"
    )

    fuel_needed_warp: int = Field(
        description="Amount Resource Mined"
    )

    fuel_needed_half_warp: int = Field(
        description="Amount Resource Mined"
    )

    fuel_needed_subwarp: int = Field(
        description="Amount Resource Mined"
    )

    ammo_for_duration: int = Field(
        description="Amount Resource Mined"
    )

    food_for_duration: int = Field(
        description="Amount Resource Mined"
    )

    resource_hardness: int = Field(
        description="Amount Resource Mined"
    )

    system_richness: int = Field(
        description="Amount Resource Mined"
    )

    mine_item: str = Field(
        description="Amount Resource Mined"
    )

    sage_resource: str = Field(
        description="Amount Resource Mined"
    )

    planet: str = Field(
        description="Amount Resource Mined"
    )

    
