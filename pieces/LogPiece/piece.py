from starflow.base_piece import BasePiece
from .models import InputModel, OutputModel
from pathlib import Path

class LogPiece(BasePiece):

    def piece_function(self, input_data: InputModel):

        # Log inputs
        msg = f"""msg: {input_data.input_str}"""
        self.logger.info(msg)

        # Return output
        return OutputModel(
            output_log=msg,
            output_str=input_data.input_str
        )
