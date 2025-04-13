from typing import Any
from .common_utils import retry_put_request
from starflow.base_piece import BasePiece
from .models import FleetStatusEnum, InputModel, OutputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import json

class StarAtlasLoadFuelPiece(BasePiece):

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

    def get_fleet_position(self, fleet_name, bearer_token) -> Any:

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        response_raw = requests.get(self.url_get_list_fleet, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        returnState = (0, 0)

        for fleet in response_raw_json:

            if fleet["label"] == fleet_name:

                return (fleet["startingCoords"]["x"], fleet["startingCoords"]["y"])
            
        return returnState

    def piece_function(self, input_data: InputModel):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        self.logger.info(f"Token for {self.username_target_var} created")

        fleet_position = self.get_fleet_position(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

        if fleet_position[0] != input_data.destination_x or fleet_position[1] != input_data.destination_y:
            raise Exception("Fleet Position not correct") 

        self.logger.info(f"")

        fleet_status = self.get_fleet_status(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

        if fleet_status == FleetStatusEnum.StarbaseLoadingBay:

            self.logger.info(f"Loading Fuel for {input_data.fleet_name} on ({input_data.destination_x}, {input_data.destination_y}), {input_data.amount}")
            url_formated_load_fuel = self.url_put_load_fuel.format(input_data.fleet_name, input_data.amount, input_data.destination_x, input_data.destination_y)
            res_action = retry_put_request(url_formated_load_fuel, client_token_loggedin)
            if not(res_action):
                raise Exception("load_fuel Error")
            
            self.logger.info(f"Fuel Loaded successfully for {input_data.fleet_name} on ({input_data.destination_x}, {input_data.destination_y}), {input_data.amount}")

            self.logger.info(f"")

        else:
            raise Exception("Fleet is in incorrect state")

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(
            amount_loaded=input_data.amount,
            destination_x=input_data.destination_x,
            destination_y=input_data.destination_y,
        )
