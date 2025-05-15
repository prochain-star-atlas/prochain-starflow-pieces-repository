from typing import Any
from starflow.base_piece import BasePiece, BaseBranchOutputModel
from .common_utils import retry_put_request
from .models import InputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import json

class StarAtlasGenericCheckPiece(BasePiece):

    def piece_function(self, input_data: InputModel):

        self.logger.info(f"")

        test_valid = input_data.value_to_test == input_data.required_field

        self.logger.info(f"Status test is: {test_valid}, test status: {input_data.value_to_test}, required status: {input_data.required_field}")

        # Return output
        return BaseBranchOutputModel(
            branch_main=test_valid
        )
