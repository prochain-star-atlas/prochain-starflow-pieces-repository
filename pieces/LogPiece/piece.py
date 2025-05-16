from starflow.base_piece import BasePiece
from .models import InputModel, OutputModel
from pathlib import Path

class LogPiece(BasePiece):

    def piece_function(self, input_data: InputModel, workspace_id):

        # Log inputs
        msg = f"""msg: {input_data.input_str}\n
msg_int: {input_data.input_int}\n
msg_float: {input_data.input_float}"""
        
        self.logger.info(msg)

        # Return output
        return OutputModel(
            output_log=msg
        )
