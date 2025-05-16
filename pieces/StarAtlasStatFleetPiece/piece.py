from typing import Any
from starflow.base_piece import BasePiece
from .common_utils import retry_put_request
from .models import InputModel, OutputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import time
import json
import math

class StarAtlasStatMiningFleetPiece(BasePiece):

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
        self.url_put_refresh_fleet = self.read_secrets('URL_PUT_REFRESH_FLEET')

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
        
    def get_fleet_statistics(self, fleet_name, bearer_token) -> Any:

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        response_raw = requests.get(self.url_get_list_fleet, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        returnFleet = {}

        for fleet in response_raw_json:

            if fleet["label"] == fleet_name:

                returnFleet = fleet

        return returnFleet
        
    def refresh_fleet_state(self, fleet_name, bearer_token):

        self.logger.info(f"Refresh Fleet State for {fleet_name}")
        url_formated_refresh_state = self.url_put_refresh_fleet.format(fleet_name)
        res_action2 = retry_put_request(url_formated_refresh_state, bearer_token)
        self.logger.info(f"Refreshed Fleet State: {res_action2}")

    def piece_function(self, input_data: InputModel, workspace_id):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        headers = {"Authorization": "Bearer " + client_token_loggedin['access_token']}
        self.logger.info(f"Token for {self.username_target_var} created")

        self.refresh_fleet_state(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

        fleet_stat = self.get_fleet_statistics(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

        self.logger.info(f"")

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(

            fleet_name=input_data.fleet_name,
            public_key=fleet_stat["publicKey"],
            state=fleet_stat["state"],
            faction=fleet_stat["faction"],
            warp_fuel_consumption_rate=fleet_stat["warpFuelConsumptionRate"],
            warp_speed=fleet_stat["warpSpeed"],
            max_warp_distance=fleet_stat["maxWarpDistance"],
            subwarp_fuel_consumption_rate=fleet_stat["subwarpFuelConsumptionRate"],
            subwarp_speed=fleet_stat["subwarpSpeed"],
            cargo_capacity=fleet_stat["cargoCapacity"],
            fuel_capacity=fleet_stat["fuelCapacity"],
            ammo_capacity=fleet_stat["ammoCapacity"],
            scan_cost=fleet_stat["scanCost"],
            require_crew=fleet_stat["requiredCrew"],
            passenger_capacity=fleet_stat["passengerCapacity"],
            crew_count=fleet_stat["crewCount"],
            rented_crew=fleet_stat["rentedCrew"],
            respawn_time=fleet_stat["respawnTime"],
            sdu_per_scan=fleet_stat["sduPerScan"],
            scan_cooldown=fleet_stat["scanCooldown"],
            warp_cooldown=fleet_stat["warpCooldown"],
            mining_rate=fleet_stat["miningRate"],
            food_consumption_rate=fleet_stat["foodConsumptionRate"],
            ammo_consumption_rate=fleet_stat["ammoConsumptionRate"],
            planet_exit_fuel_amount=fleet_stat["planetExitFuelAmount"],
            food_cnt=fleet_stat["foodCnt"],
            sdu_cnt=fleet_stat["sduCnt"],
            fuel_cnt=fleet_stat["fuelCnt"],
            ammo_cnt=fleet_stat["ammoCnt"]
            
        )
