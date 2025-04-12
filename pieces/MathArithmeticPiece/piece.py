from starflow.base_piece import BasePiece
from .models import InputEnum, InputModel, OutputModel
from pathlib import Path


class LogPiece(BasePiece):

    def piece_function(self, input_data: InputModel):

        result = 0

        if input_data.operation_enum == InputEnum.addition:
            result = input_data.left_input + input_data.right_input

        if input_data.operation_enum == InputEnum.divide:
            result = input_data.left_input / input_data.right_input

        if input_data.operation_enum == InputEnum.multiply:
            result = input_data.left_input * input_data.right_input

        if input_data.operation_enum == InputEnum.substract:
            result = input_data.left_input - input_data.right_input

        # Return output
        return OutputModel(
            result_output=result
        )
