from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from decimal import *


class InputEnum(str, Enum):
    addition = "addition"
    substract = "substract"
    multiply = "multiply"
    divide = "divide"


class InputModel(BaseModel):
    """
    MathArithmeticPiece Input Model
    """
    left_input_int: Optional[int] = Field(
        default=0,
        description='Left Input Int.'
    )
    right_input_int: Optional[int] = Field(
        default=0,
        description='Right Input Int.'
    )
    left_input_float: Optional[float] = Field(
        default=0,
        description='Left Input Float.'
    )
    right_input_float: Optional[float] = Field(
        default=0,
        description='Right Input Float.'
    )
    operation_enum: InputEnum = Field(
        default=InputEnum.addition,
        description='Input addition.'
    )
    
class OutputModel(BaseModel):
    """
    MathArithmeticPiece Output Model
    """
    result_output_float: float = Field(
        description='Result from operation.'
    )
    result_output_int: int = Field(
        description='Result from operation.'
    )
