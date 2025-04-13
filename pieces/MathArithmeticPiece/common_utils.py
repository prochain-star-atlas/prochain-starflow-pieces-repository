from typing import Any
from starflow.base_piece import BasePiece
from .models import FleetStatusEnum, InputModel, OutputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import json


def retry_put_request(self, url_formated, bearer_token):
    headers = {"Authorization": "Bearer " + bearer_token['access_token']}
    retries = 0
    success = False
    wait_time = 5
    while not success and retries <= 5:
        try:
            response_raw = requests.put(url_formated, headers=headers, verify=False, timeout=120)
            response_raw_json = response_raw.json()
            success = True
            self.logger.info("Successfully executed !")
            json_formatted_str = json.dumps(response_raw_json, indent=2)
            self.logger.info(json_formatted_str)           
            
        except Exception as e:
            self.logger.error(f"Waiting {wait_time} secs and re-trying...")
            timew.sleep(wait_time)
            retries += 1

    return success
