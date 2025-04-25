from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class InputModel(BaseModel):
    """
    Star Atlas Planet Cargo Check Piece Input Model
    """

    location_x: int = Field(
        default=0,
        description="location_x"
    )

    location_y: int = Field(
        default=0,
        description="location_y"
    )

    resource_mint: str = Field(
        default="",
        description="resource_mint",
    )

    resource_amount: int = Field(
        default=0,
        description="resource_amount In Planet",
    )

