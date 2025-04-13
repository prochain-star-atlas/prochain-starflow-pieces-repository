from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from decimal import *

class InputModel(BaseModel):
    """
    MathArithmeticPiece Input Model
    """
    input_int: int = Field(
        default=0,
        description='Input Int.'
    )
    
class OutputModel(BaseModel):
    """
    MathArithmeticPiece Output Model
    """
    result_output_float: float = Field(
        description='Result from operation.'
    )
