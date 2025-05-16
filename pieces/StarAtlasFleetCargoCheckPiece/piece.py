from typing import Any
from starflow.base_piece import BasePiece, BaseBranchOutputModel
from .common_utils import retry_put_request
from .models import InputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import json

class StarAtlasFleetCargoCheckPiece(BasePiece):

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
        
    def get_fleet_all_cargo_and_fuel_ammo(self, fleet_name, bearer_token):

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        url_formated_list_fleet = self.url_get_list_fleet.format(fleet_name)
        response_raw = requests.get(url_formated_list_fleet, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        cargo_list = []
        fuel_amount = 0
        ammo_amount = 0

        for fleet_item in response_raw_json:
            if fleet_item["label"] == fleet_name:
                fuel_amount = fleet_item["fuelCnt"]
                ammo_amount = fleet_item["ammoCnt"]
                for fleet_cargo in fleet_item["fleetCargo"]:
                    if fleet_cargo["pubKey"] != fleet_item["fuelToken"] and fleet_cargo["pubKey"] != fleet_item["ammoToken"]:
                        cargo_list.append(fleet_cargo)

        return (fuel_amount, ammo_amount, cargo_list)

    def get_fleet_cargo_amount_request(self, fleet_name, resource_item, bearer_token):

        all_cargo = self.get_fleet_all_cargo_and_fuel_ammo(fleet_name, bearer_token)

        for cargo_item in all_cargo[2]:
            if cargo_item["tokenMint"] == resource_item:
                return cargo_item["tokenAmount"]

        return 0

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
        self.logger.info(f"Token for {self.username_target_var} created")

        self.refresh_fleet_state(fleet_name=input_data.fleet_name, bearer_token=client_token_loggedin)

        self.logger.info(f"")

        all_cargos = self.get_fleet_all_cargo_and_fuel_ammo(input_data.fleet_name, bearer_token=client_token_loggedin)
        test_check_res = False

        if input_data.fuel_amount is not None and input_data.fuel_amount > 0:
            fuel_cargo = self.get_fleet_all_cargo_and_fuel_ammo(input_data.fleet_name, bearer_token=client_token_loggedin)
            test_check_res = fuel_cargo[0] >= input_data.fuel_amount
        elif input_data.ammo_amount is not None and input_data.ammo_amount > 0:
            ammo_cargo = self.get_fleet_all_cargo_and_fuel_ammo(input_data.fleet_name, bearer_token=client_token_loggedin)
            test_check_res = ammo_cargo[1] >= input_data.ammo_amount
        elif input_data.resource_amount is not None and input_data.resource_amount > 0:
            amount_cargo = self.get_fleet_cargo_amount_request(input_data.fleet_name, resource_item=input_data.resource_mint, bearer_token=client_token_loggedin)
            test_check_res = amount_cargo >= input_data.resource_amount
            
        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return BaseBranchOutputModel(
            branch_main=test_check_res
        )
