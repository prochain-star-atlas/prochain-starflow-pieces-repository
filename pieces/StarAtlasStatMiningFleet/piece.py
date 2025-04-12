from typing import Any
from starflow.base_piece import BasePiece
from .models import FleetStatusEnum, InputModel, OutputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import time
import json

class StarAtlasStatMiningPiece(BasePiece):

    def read_secrets(self, var_name):
        with open("/var/mount_secrets/" + var_name) as f:
            file_content = f.read()
            return file_content

    def init_piece(self):

        self.server_url_var = self.read_secrets('OPEN_ID_SERVER_URL')
        self.client_id_var = self.read_secrets('OPEN_ID_CLIENT_ID')
        self.realm_name_var = self.read_secrets('OPEN_ID_REALM_NAME')
        self.client_secret_var = self.read_secrets('OPEN_ID_CLIENT_SECRET')
        self.su_username_var = self.read_secrets('OPEN_ID_USERNAME_SERVICE_USER')
        self.su_password_var = self.read_secrets('OPEN_ID_PASSWORD_SERVICE_USER')
        self.username_target_var = os.environ['OPEN_ID_USERNAME_TARGET']
        self.url_put_start_mining = self.read_secrets('URL_PUT_START_MINING')
        self.url_put_stop_mining = self.read_secrets('URL_PUT_STOP_MINING')
        self.url_get_fleet_mining_calculation = self.read_secrets('URL_GET_FLEET_MINING_CALCULATION')
        self.url_get_list_fleet = self.read_secrets('URL_GET_LIST_FLEET')

        self.keycloak_openid = KeycloakOpenID(server_url=self.server_url_var,
                                 client_id=self.client_id_var,
                                 realm_name=self.realm_name_var,
                                 client_secret_key=self.client_secret_var,
                                 verify=False)

    def openid_get_token(self) -> Any:
        token = self.keycloak_openid.token(username=self.su_username_var, password=self.su_password_var)
        return token

    def openid_logout_user(self, token_logged_in):
        self.keycloak_openid.logout(refresh_token=token_logged_in["refresh_token"])

    def openid_impersonate_user_token_keycloak(self, token_logged_in) -> Any:
        token_impersonated = self.keycloak_openid.exchange_token(token=token_logged_in["access_token"], audience=self.client_id_var, subject=self.username_target_var)
        return token_impersonated
        
    def retry_put_request(self, url_formated, bearer_token):
        headers = {"Authorization": "Bearer " + bearer_token['access_token']}
        retries = 0
        success = False
        wait_time = 5
        while not success and retries <= 5:
            try:
                response_raw = requests.put(url_formated, headers=headers, verify=False)
                response_raw_json = response_raw.json()

                if response_raw_json is not None and response_raw_json.meta is not None and response_raw_json.meta.err is None:
                    success = True
                    self.logger.info("Successfully executed !")
                    json_formatted_str = json.dumps(response_raw_json, indent=2)
                    self.logger.info(json_formatted_str)
                    
                else:
                    self.logger.error(f"Waiting {wait_time} secs and re-trying...")
                    #self.logger.info(f"json: {response_raw_json}")
                    timew.sleep(wait_time)
                    retries += 1                
                
            except Exception as e:
                self.logger.error(f"Waiting {wait_time} secs and re-trying...")
                timew.sleep(wait_time)
                retries += 1

        return success

    def get_fleet_mining_stat_request(self, fleet_name, bearer_token):
        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        url_formated_list_fleet = self.url_get_fleet_mining_calculation.format(fleet_name)
        response_raw = requests.get(url_formated_list_fleet, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        return response_raw_json.result
        
    def piece_function(self, input_data: InputModel):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        headers = {"Authorization": "Bearer " + client_token_loggedin['access_token']}
        self.logger.info(f"Token for {self.username_target_var} created")

        fleet_mining_stat = self.get_fleet_mining_stat_request(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

        self.logger.info(f"")

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(
            fleet_name=input_data.fleet_name,
            planet_name=fleet_mining_stat.planetName,
            location_x=fleet_mining_stat.destX,
            location_y=fleet_mining_stat.destY,
            food_consumption_rate=fleet_mining_stat.foodConsumptionRate,
            ammo_consumption_rate=fleet_mining_stat.ammoConsumptionRate,
            mining_rate=fleet_mining_stat.miningRate,
            max_mining_duration=fleet_mining_stat.maxMiningDuration,
            mine_time_passed=fleet_mining_stat.mineTimePassed,
            mine_time_in_minutes_passed=fleet_mining_stat.mineTimeInMinutesPassed,
            food_consumed=fleet_mining_stat.foodConsumed,
            ammo_consumed=fleet_mining_stat.ammoConsumed,
            resource_mined=fleet_mining_stat.resourceMined,
            time_food_remaining=fleet_mining_stat.timeFoodRemaining,
            time_food_in_minutes_remaining=fleet_mining_stat.timeFoodInMinutesRemaining,
            time_ammo_remaining=fleet_mining_stat.timeAmmoRemaining,
            time_ammo_in_minutes_remaining=fleet_mining_stat.timeAmmoInMinutesRemaining,
            sim_current_cargo=fleet_mining_stat.simCurrentCargo,
            time_cargo_remaining=fleet_mining_stat.timeCargoRemaining,
            time_cargo_in_minutes_remaining=fleet_mining_stat.timeCargoInMinutesRemaining,
            time_limit=fleet_mining_stat.timeLimit,
            time_limit_in_minutes=fleet_mining_stat.timeLimitInMinutes,
            mine_end=fleet_mining_stat.mineEnd,
            mine_end_string=fleet_mining_stat.mineEndString,
            mine_end_iso_string=fleet_mining_stat.mineEndIsoString,
            sage_resource_mined=fleet_mining_stat.sageResourceMined,
            system_richness=fleet_mining_stat.systemRichness,
            resource_hardness=fleet_mining_stat.resourceHardness,
        )
