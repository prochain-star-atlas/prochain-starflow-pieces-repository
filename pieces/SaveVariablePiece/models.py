from typing import Optional
from pydantic import BaseModel, Field


class InputModel(BaseModel):
    """
    Set Variable Piece Input Model
    """

    key: str = Field(
        default="",
        description="Variable Key",
    )

    str_value: Optional[str] = Field(
        default="",
        description="Value String",
    )

    int_value: Optional[int] = Field(
        default=0,
        description="Value Int",
    )

    float_value: Optional[float] = Field(
        default=0,
        description="Value Float",
    )


class OutputModel(BaseModel):
    """
    Set Variable Piece Output Model
    """
    key: str = Field(
        description="Variable Key",
    )

    str_value: Optional[str] = Field(
        description="Value String",
    )

    int_value: Optional[int] = Field(
        description="Value Int",
    )

    float_value: Optional[float] = Field(
        description="Value Float",
    )
