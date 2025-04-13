from typing import Any
from starflow.base_piece import BasePiece, BaseBranchOutputModel
from .models import InputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import json

class StarAtlasFleetLocationCheckPiece(BasePiece):

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
        self.url_put_start_undock = self.read_secrets('URL_PUT_START_UNDOCK')
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

    def get_fleet_location(self, fleet_name, bearer_token):

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        response_raw = requests.get(self.url_get_list_fleet, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        x = 0
        y = 0

        for fleet in response_raw_json:

            if fleet["label"] == fleet_name:

                if fleet["state"] == "StarbaseLoadingBay":
                    x = fleet["startingCoords"]["x"]
                    y = fleet["startingCoords"]["y"]
                elif fleet["state"] == "ReadyToExitWarp":
                    x = fleet["startingCoords"]["x"]
                    y = fleet["startingCoords"]["y"]
                elif fleet["state"] == "MineAsteroid":
                    x = fleet["startingCoords"]["x"]
                    y = fleet["startingCoords"]["y"]
                elif fleet["state"] == "MoveWarp":
                    x = fleet["endingCoords"]["x"]
                    y = fleet["endingCoords"]["y"]
                elif fleet["state"] == "MoveSubwarp":
                    x = fleet["endingCoords"]["x"]
                    y = fleet["endingCoords"]["y"]
                elif fleet["state"] == "Respawn":
                    x = fleet["startingCoords"]["x"]
                    y = fleet["startingCoords"]["y"]
                elif fleet["state"] == "StarbaseUpgrade":
                    x = fleet["startingCoords"]["x"]
                    y = fleet["startingCoords"]["y"]
                else:
                    x = fleet["startingCoords"]["x"]
                    y = fleet["startingCoords"]["y"]

        return (x,y)

    def piece_function(self, input_data: InputModel):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        self.logger.info(f"Token for {self.username_target_var} created")

        self.logger.info(f"")

        fleet_location = self.get_fleet_location(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)
        test_valid = input_data.destination_x == fleet_location[0] and input_data.destination_y == fleet_location[1]

        self.logger.info(f"Status test is: {test_valid}, required location x: {input_data.destination_x}, required location y: {input_data.destination_y}")

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return BaseBranchOutputModel(
            branch_main=test_valid
        )
