from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class CargoModel(BaseModel):

    cargo_label: str = Field(
        default="",
        description="Cargo Label",
    )

    cargo_mint: str = Field(
        default="",
        description="Cargo Mint",
    )

    cargo_amount: int = Field(
        default="",
        description="Cargo Amount",
    )

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

    cargo_list: List[CargoModel] = Field(
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

    resource_mint_requested: str = Field(
        description="Resource Mint Requested"
    )

    resource_amount_requested: int = Field(
        default=0,
        description="Amount Resource Requested"
    )

    
