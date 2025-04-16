from starflow.base_piece import BasePiece
from .models import InputEnum, InputModel, OutputModel
from pathlib import Path
import math

class MathArithmeticPiece(BasePiece):

    def piece_function(self, input_data: InputModel):

        result_int = 0
        result_float = 0

        if input_data.left_input_int is not None and input_data.right_input_int is not None:
            if input_data.operation_enum == InputEnum.addition:
                result_int = input_data.left_input_int + input_data.right_input_int

            if input_data.operation_enum == InputEnum.divide:
                result_int = math.ceil(input_data.left_input_int / input_data.right_input_int)

            if input_data.operation_enum == InputEnum.multiply:
                result_int = input_data.left_input_int * input_data.right_input_int

            if input_data.operation_enum == InputEnum.substract:
                result_int = input_data.left_input_int - input_data.right_input_int

        if input_data.left_input_float is not None and input_data.right_input_float is not None:
            if input_data.operation_enum == InputEnum.addition:
                result_float = input_data.left_input_float + input_data.right_input_float

            if input_data.operation_enum == InputEnum.divide:
                result_float = input_data.left_input_float / input_data.right_input_float

            if input_data.operation_enum == InputEnum.multiply:
                result_float = input_data.left_input_float * input_data.right_input_float

            if input_data.operation_enum == InputEnum.substract:
                result_float = input_data.left_input_float - input_data.right_input_float

        # Return output
        return OutputModel(
            result_output_int=result_int,
            result_output_float=result_float
        )
