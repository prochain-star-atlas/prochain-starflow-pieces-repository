from typing import Optional
from pydantic import BaseModel, Field


class InputModel(BaseModel):
    """
    Read Variable Piece Input Model
    """

    key: str = Field(
        default="",
        description="Variable Key",
    )


class OutputModel(BaseModel):
    """
    Read Variable Piece Output Model
    """
    
    str_value: Optional[str] = Field(
        description="Value String",
    )

    int_value: Optional[int] = Field(
        description="Value Int",
    )

    float_value: Optional[float] = Field(
        description="Value Float",
    )
