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

class StarAtlasMiningPiece(BasePiece):

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
        self.url_get_future_mining_stats = self.read_secrets('URL_GET_FLEET_FUTURE_MINING_STATISTICS')

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

    def get_future_mining_calculation(self, fleet_name, resourceMint, starbaseX, starbaseY, planetX, planetY, bearer_token) -> Any:

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        url_formated_mining_calculation = self.url_get_future_mining_stats.format(fleet_name, resourceMint, starbaseX, starbaseY, planetX, planetY)
        response_raw = requests.get(url_formated_mining_calculation, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        return response_raw_json.result

    def piece_function(self, input_data: InputModel):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        headers = {"Authorization": "Bearer " + client_token_loggedin['access_token']}
        self.logger.info(f"Token for {self.username_target_var} created")

        future_mining_calc = self.response_raw_json(fleet_name=input_data.fleet_name, 
                                                resourceMint=input_data.resource_mint, 
                                                starbaseX=input_data.starbase_x, 
                                                starbaseY=input_data.starbase_y, 
                                                planetX=input_data.planet_x, 
                                                planetY=input_data.planet_y, 
                                                bearer_token=client_token_loggedin)

        self.logger.info(f"")

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(
            fleet_name=input_data.fleet_name,
            resource_mint_mined=input_data.resource_mint,
            mining_duration=future_mining_calc.miningDuration,
            mining_duration_in_minutes=future_mining_calc.miningDurationInMinutes,
            amount_mined=future_mining_calc.amountMined,
            fuel_needed_warp=future_mining_calc.fuelNeededWarp,
            fuel_needed_half_warp=future_mining_calc.fuelNeededHalfWarp,
            fuel_needed_subwarp=future_mining_calc.fuelNeededSubWarp,
            ammo_for_duration=future_mining_calc.ammoForDuration,
            food_for_duration=future_mining_calc.foodForDuration,
            resource_hardness=future_mining_calc.resourceHardness,
            system_richness=future_mining_calc.systemRichness,
            mine_item=future_mining_calc.mineItem,
            sage_resource=future_mining_calc.sageResource,
            planet=future_mining_calc.planet
        )
