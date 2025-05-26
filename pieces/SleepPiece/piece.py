from starflow.base_piece import BasePiece
from .models import InputModel, OutputModel
from time import sleep

class SleepPiece(BasePiece):

    def piece_function(self, input_data: InputModel, workspace_id):

        self.logger.info(f"Sleeping for {input_data.sleep_time} seconds")
        sleep(float(input_data.sleep_time))

        message = f"Sleep piece executed successfully for {input_data.sleep_time} seconds"

        # Return output
        return OutputModel(
            message=message,
        )
