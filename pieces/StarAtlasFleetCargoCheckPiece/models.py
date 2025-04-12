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
        description="Resource to request amount",
    )

    resource_amount: Optional[int] = Field(
        default="",
        description="Resource Amount In Fleet",
    )

    fuel_amount: Optional[int] = Field(
        default="",
        description="Resource Amount In Fleet",
    )

    ammo_amount: Optional[int] = Field(
        default="",
        description="Resource Amount In Fleet",
    )

