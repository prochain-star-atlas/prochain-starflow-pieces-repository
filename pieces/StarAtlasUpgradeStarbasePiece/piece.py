from starflow.base_piece import BasePiece
from .models import InputModel, OutputModel
from time import sleep


class StarAtlasUpgradeStarbasePiece(BasePiece):

    def read_secrets(self, var_name):
        with open("/var/mount_secrets/" + var_name) as f:
            file_content = f.read()
            return file_content

    def piece_function(self, input_data: InputModel, workspace_id):

        self.logger.info(f"Sleeping for {input_data.sleep_time} seconds")
        sleep(input_data.sleep_time)
        message = f"Sleep piece executed successfully for {input_data.sleep_time} seconds"
        self.logger.info(message)

        # Return output
        return OutputModel(
            message=message,
        )
