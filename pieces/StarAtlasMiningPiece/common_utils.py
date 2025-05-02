from typing import Any
from time import sleep
import time as timew
import requests
import json
import logging

logger = logging.getLogger(__name__)

def retry_put_request(url_formated, bearer_token):
    headers = {"Authorization": "Bearer " + bearer_token['access_token']}
    retries = 0
    success = False
    wait_time = 5
    while not success and retries <= 10:
        try:
            response_raw = requests.put(url_formated, headers=headers, verify=False, timeout=120)
            response_raw_json = response_raw.json()
            success = True
            logger.info("Successfully executed !")
            json_formatted_str = json.dumps(response_raw_json, indent=2)
            logger.info(json_formatted_str)           
            
        except Exception as e:
            logger.error(f"Waiting {wait_time} secs and re-trying...")
            timew.sleep(wait_time)
            retries += 1

    return success
