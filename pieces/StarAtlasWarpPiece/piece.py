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

class StarAtlasWarpPiece(BasePiece):

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
        self.url_put_start_warp = self.read_secrets('URL_PUT_START_WARP')
        self.url_put_exit_warp = self.read_secrets('URL_PUT_START_EXITWARP')
        self.url_get_fleet_movement_calculation = self.read_secrets('URL_GET_FLEET_MOVEMENT_CALCULATION')
        self.url_get_list_fleet = self.read_secrets('URL_GET_LIST_FLEET')
        self.url_put_refresh_fleet = self.read_secrets('URL_PUT_REFRESH_FLEET')
        self.url_get_fleet_future_movement_statistics = self.read_secrets('URL_GET_FLEET_FUTURE_MOVEMENT_STATISTICS')

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

        returnState = FleetStatusEnum.Respawn

        for fleet in response_raw_json:

            if fleet["label"] == fleet_name:

                returnState = FleetStatusEnum[fleet["state"]]

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
    
    def get_fleet_warpCooldown(self, fleet_name, bearer_token) -> Any:

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        response_raw = requests.get(self.url_get_list_fleet, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        returnState = 0

        for fleet in response_raw_json:
            if fleet["label"] == fleet_name:
                returnState = fleet["warpCooldown"]

        return returnState

    def get_fleet_future_movement_statistics_request(self, fleet_name, startX, startY, destX, destY, bearer_token):
        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        url_formated_future_mov_stats = self.url_get_fleet_future_movement_statistics.format(fleet_name, startX, startY, destX, destY)
        response_raw = requests.get(url_formated_future_mov_stats, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        return response_raw_json["result"]

    def refresh_fleet_state(self, fleet_name, bearer_token):

        self.logger.info(f"Refresh Fleet State for {fleet_name}")
        url_formated_refresh_state = self.url_put_refresh_fleet.format(fleet_name)
        res_action2 = retry_put_request(url_formated_refresh_state, bearer_token)
        self.logger.info(f"Refreshed Fleet State: {res_action2}")

    def piece_function(self, input_data: InputModel):

        self.init_piece()
        
        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        headers = {"Authorization": "Bearer " + client_token_loggedin['access_token']}
        self.logger.info(f"Token for {self.username_target_var} created")

        self.refresh_fleet_state(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

        fleet_position = self.get_fleet_position(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

        if fleet_position[0] == input_data.destination_x and fleet_position[1] == input_data.destination_y:
            return OutputModel(
                fleet_name=input_data.fleet_name,
                destination_x=input_data.destination_x,
                destination_y=input_data.destination_y,
            )   

        fleet_status = self.get_fleet_status(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

        self.logger.info(f"")
        warpCooldown = self.get_fleet_warpCooldown(input_data.fleet_name, bearer_token=client_token_loggedin)

        if fleet_status == FleetStatusEnum.Idle:

            future_mov = self.get_fleet_future_movement_statistics_request(input_data.fleet_name, fleet_position[0], fleet_position[1], input_data.destination_x, input_data.destination_y, client_token_loggedin)

            for wp in future_mov["warpPoints"]["allWarpPoints"]:

                if wp[0] == fleet_position[0] and wp[1] == fleet_position[1]:
                    continue

                url_formated_start_warp = self.url_put_start_warp.format(input_data.fleet_name, wp[0], wp[1])
                res_action1 = retry_put_request(url_formated_start_warp, client_token_loggedin)

                if not(res_action1):
                    raise Exception("start_warp Error")                

                self.refresh_fleet_state(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

                self.logger.info(f"Calculate Movement Duration")
                url_formatted_fleet_movement_calculation = self.url_get_fleet_movement_calculation.format(input_data.fleet_name)
                headers = {"Authorization": "Bearer " + client_token_loggedin['access_token']}
                response_fleet_movement_calculation = requests.get(url_formatted_fleet_movement_calculation, headers=headers, verify=False)
                response_fleet_movement_calculation_json = response_fleet_movement_calculation.json()

                self.openid_logout_user(client_token_loggedin)
                self.openid_logout_user(su_token_loggedin)

                wait_time_movement = response_fleet_movement_calculation_json["result"]["endTimeRemaining"]
                self.logger.info(f"waiting movement for {wait_time_movement} seconds")
                time.sleep(wait_time_movement)

                su_token_loggedin = self.openid_get_token()
                client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
                
                url_formated_put_exit_warp = self.url_put_exit_warp.format(input_data.fleet_name)
                res_action2 = retry_put_request(url_formated_put_exit_warp, client_token_loggedin)

                if not(res_action2):
                    raise Exception("exit_warp Error")                
                
                self.refresh_fleet_state(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

                if wp[0] == input_data.destination_x and wp[1] == input_data.destination_y:
                    self.logger.info(f"fleet arrived at destination")
                else:
                    self.openid_logout_user(client_token_loggedin)
                    self.openid_logout_user(su_token_loggedin)

                    self.logger.info(f"waiting cooldown for {warpCooldown} seconds")
                    time.sleep(warpCooldown)

                    su_token_loggedin = self.openid_get_token()
                    client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)


        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(
            fleet_name=input_data.fleet_name,
            destination_x=input_data.destination_x,
            destination_y=input_data.destination_y,
        )
