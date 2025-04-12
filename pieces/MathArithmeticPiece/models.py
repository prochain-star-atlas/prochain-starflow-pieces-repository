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
    left_input: Decimal = Field(
        default="",
        description='Left Input.'
    )
    right_input: Decimal = Field(
        default="",
        description='Right Input.'
    )
    operation_enum: InputEnum = Field(
        default=InputEnum.addition,
        description='Input addition.'
    )
    
class OutputModel(BaseModel):
    """
    MathArithmeticPiece Output Model
    """
    result_output: Decimal = Field(
        description='Result from operation.'
    )
