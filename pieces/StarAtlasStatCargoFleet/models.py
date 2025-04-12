from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class InputModel(BaseModel):
    """
    StarAtlas Mining Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    resource_mint: Optional[str] = Field(
        default="",
        description="Resource to request amount",
    )

class OutputModel(BaseModel):
    """
    StarAtlas Mining Piece Output Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    cargo_list: List[(str, int)] = Field(
        description='Cargo List.'
    )

    fuel_amount: int = Field(
        default="",
        description="Fuel Amount In Fleet",
    )

    ammo_amount: int = Field(
        default="",
        description="Ammo Amount In Fleet",
    )

    resource_mint_requested: Optional[str] = Field(
        description="Resource Mint Requested"
    )

    resource_amount_requested: Optional[int] = Field(
        description="Amount Resource Requested"
    )

    
