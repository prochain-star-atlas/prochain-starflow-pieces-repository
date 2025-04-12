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

    def get_fleet_all_cargo_and_fuel_ammo(self, fleet_name, bearer_token):

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        url_formated_list_fleet = self.url_get_list_fleet.format(fleet_name)
        response_raw = requests.get(url_formated_list_fleet, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        cargo_list = []
        fuel_amount = 0
        ammo_amount = 0

        for fleet_item in response_raw_json:
            if fleet_item.label == fleet_name:
                fuel_amount = fleet_item.fuelCnt
                ammo_amount = fleet_item.ammoCnt
                for fleet_cargo in fleet_item.fleetCargo:
                    if fleet_cargo.pubKey != fleet_item.fuelToken and fleet_cargo.pubKey != fleet_item.ammoToken:
                        cargo_list.append(fleet_cargo)

        return (fuel_amount, ammo_amount, cargo_list)

    def get_fleet_cargo_amount_request(self, fleet_name, resource_item, bearer_token):

        all_cargo = self.get_fleet_all_cargo_and_fuel_ammo(fleet_name, bearer_token)

        for cargo_item in all_cargo[2]:
            if cargo_item.tokenMint == resource_item:
                return cargo_item.tokenAmount

        return 0

    def piece_function(self, input_data: InputModel):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        headers = {"Authorization": "Bearer " + client_token_loggedin['access_token']}
        self.logger.info(f"Token for {self.username_target_var} created")

        amount_cargo_requested = 0
        mint_cargo_requested = ""

        self.logger.info(f"")

        all_cargos = self.get_fleet_all_cargo_and_fuel_ammo(input_data.fleet_name, bearer_token=client_token_loggedin)

        if input_data.resource_mint is not None:
            amount_cargo = self.get_fleet_cargo_amount_request(input_data.fleet_name, input_data.resource_mint, bearer_token=client_token_loggedin)
            mint_cargo_requested = ""
            
        c_list = []
        for ac in all_cargos[2]:
            c_list.append((ac.tokenMint, ac.tokenAmount))

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(
            fleet_name=input_data.fleet_name,
            cargo_list=c_list,
            fuel_amount=all_cargos[0],
            ammo_amount=all_cargos[1],
            resource_mint_requested=mint_cargo_requested,
            resource_amount_requested=amount_cargo
        )
