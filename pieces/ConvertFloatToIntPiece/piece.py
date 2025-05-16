from starflow.base_piece import BasePiece
from .models import InputModel, OutputModel
from pathlib import Path
import math

class ConvertFloatToIntPiece(BasePiece):

    def piece_function(self, input_data: InputModel, workspace_id):

        # Return output
        return OutputModel(
            result_output_int=math.ceil(input_data.input_float)
        )
