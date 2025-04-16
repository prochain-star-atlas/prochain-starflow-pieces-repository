from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class InputModel(BaseModel):
    """
    Star Atlas Fleet Cargo Check Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    resource_mint: str = Field(
        default="",
        description="resource_mint",
    )

    resource_amount: int = Field(
        default=0,
        description="resource_amount In Fleet",
    )

    fuel_amount: int = Field(
        default=0,
        description="fuel_amount In Fleet",
    )

    ammo_amount: int = Field(
        default=0,
        description="ammo_amount In Fleet",
    )

