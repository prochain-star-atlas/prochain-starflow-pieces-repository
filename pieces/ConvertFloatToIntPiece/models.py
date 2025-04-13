from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from decimal import *

class InputModel(BaseModel):
    """
    ConvertFloatToIntPiece Input Model
    """
    input_float: float = Field(
        default=0,
        description='Input Float.'
    )
    
class OutputModel(BaseModel):
    """
    ConvertFloatToIntPiece Output Model
    """
    result_output_int: int = Field(
        description='Result from operation.'
    )