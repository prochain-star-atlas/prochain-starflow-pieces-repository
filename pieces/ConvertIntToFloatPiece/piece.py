from starflow.base_piece import BasePiece
from .models import InputModel, OutputModel
from pathlib import Path
import math

class ConvertIntToFloatPiece(BasePiece):

    def piece_function(self, input_data: InputModel):

        # Return output
        return OutputModel(
            result_output_float=float(input_data.input_int)
        )
