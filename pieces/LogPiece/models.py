from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
from datetime import datetime, time, date

class InputModel(BaseModel):
    """
    LogPiece Input Model
    """
    input_str: str = Field(
        default="default value",
        description='Input string to be logged.'
    )
    input_int: int = Field(
        default=0,
        description='Input string to be logged.'
    )
    input_float: float = Field(
        default=0,
        description='Input string to be logged.'
    )


class OutputModel(BaseModel):
    """
    LogPiece Output Model
    """
    output_log: str = Field(
        description='All values logged.'
    )
