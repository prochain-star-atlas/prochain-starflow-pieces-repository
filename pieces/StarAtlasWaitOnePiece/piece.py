from typing import Any
from starflow.base_piece import BasePiece
from .models import InputModel, OutputModel

class StarAtlasWaitOnePiece(BasePiece):       

    def piece_function(self, input_data: InputModel, workspace_id):

        # Return output
        return OutputModel(
            output="success"
        )
