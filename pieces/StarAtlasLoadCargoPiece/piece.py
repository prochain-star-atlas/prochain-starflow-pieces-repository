from typing import Any
from starflow.base_piece import BasePiece
from .models import FleetStatusEnum, InputModel, OutputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import json

class StarAtlasLoadCargoPiece(BasePiece):

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
        self.url_put_load_cargo = self.read_secrets('URL_PUT_LOAD_CARGO')
        self.url_put_load_ammo = self.read_secrets('URL_PUT_LOAD_AMMO')
        self.url_put_load_fuel = self.read_secrets('URL_PUT_LOAD_FUEL')
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

    def get_fleet_status(self, fleet_name, bearer_token) -> FleetStatusEnum:

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        response_raw = requests.get(self.url_get_list_fleet, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        returnState = FleetStatusEnum.Idle

        for fleet in response_raw_json:

            if fleet["label"] == fleet_name:

                if fleet["state"] == "StarbaseLoadingBay":
                    returnState = FleetStatusEnum.StarbaseLoadingBay
                elif fleet["state"] == "ReadyToExitWarp":
                    returnState = FleetStatusEnum.ReadyToExitWarp
                elif fleet["state"] == "MineAsteroid":
                    returnState = FleetStatusEnum.MineAsteroid
                elif fleet["state"] == "MoveWarp":
                    returnState = FleetStatusEnum.MoveWarp
                elif fleet["state"] == "MoveSubwarp":
                    returnState = FleetStatusEnum.MoveSubwarp
                elif fleet["state"] == "Respawn":
                    returnState = FleetStatusEnum.Respawn
                elif fleet["state"] == "StarbaseUpgrade":
                    returnState = FleetStatusEnum.StarbaseUpgrade
                else:
                    returnState = FleetStatusEnum.Idle

        return returnState

    def piece_function(self, input_data: InputModel):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        self.logger.info(f"Token for {self.username_target_var} created")

        self.logger.info(f"")

        fleet_status = self.get_fleet_status(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

        if fleet_status == FleetStatusEnum.StarbaseLoadingBay:

            self.logger.info(f"Loading Cargo for {input_data.fleet_name} on ({input_data.destination_x}, {input_data.destination_y}), {input_data.amount} {input_data.resource_mint}")
            if input_data.resource_mint == "ammoK8AkX2wnebQb35cDAZtTkvsXQbi82cGeTnUvvfK":
                url_formated_load_ammo = self.url_put_load_ammo.format(input_data.fleet_name, input_data.resource_mint, input_data.amount, input_data.destination_x, input_data.destination_y)
                res_action = self.retry_put_request(url_formated_load_ammo, client_token_loggedin)
                if not(res_action):
                    raise Exception("load_ammo Error") 
            elif input_data.resourceMint == "fueL3hBZjLLLJHiFH9cqZoozTG3XQZ53diwFPwbzNim":
                url_formated_load_fuel = self.url_put_load_fuel.format(input_data.fleet_name, input_data.resource_mint, input_data.amount, input_data.destination_x, input_data.destination_y)
                res_action = self.retry_put_request(url_formated_load_fuel, client_token_loggedin)
                if not(res_action):
                    raise Exception("load_fuel Error") 
            else:
                url_formated_load_cargo = self.url_put_load_cargo.format(input_data.fleet_name, input_data.resource_mint, input_data.amount, input_data.destination_x, input_data.destination_y)
                res_action = self.retry_put_request(url_formated_load_cargo, client_token_loggedin)
                if not(res_action):
                    raise Exception("load_cargo Error") 
            
            self.logger.info(f"Cargo Loaded successfully for {input_data.fleet_name} on ({input_data.destination_x}, {input_data.destination_y}), {input_data.amount} {input_data.resource_mint}")

            self.logger.info(f"")

        else:
            raise Exception("Fleet is in incorrect state")

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(
            destination_x=input_data.destination_x,
            destination_y=input_data.destination_y,
        )
