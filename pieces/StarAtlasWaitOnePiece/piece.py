from typing import Any
from .common_utils import retry_put_request
from starflow.base_piece import BasePiece
from .models import FleetStatusEnum, InputModel, OutputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import time
import json

class StarAtlasWaitOnePiece(BasePiece):       

    def piece_function(self, input_data: InputModel):

        # Return output
        return OutputModel(
            output="success"
        )
