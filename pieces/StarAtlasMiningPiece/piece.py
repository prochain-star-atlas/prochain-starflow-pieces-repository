from typing import Any
from starflow.base_piece import BasePiece
from .models import InputModel, OutputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import time

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
                response_raw = requests.put(url_formated, headers=headers)
                response_raw_json = response_raw.json()

                if response_raw_json is not None and response_raw_json.meta is not None and response_raw_json.meta.err is None:
                    success = True
                    self.logger.info("Successfully executed !")
                    #self.logger.info(response_raw_json)
                    
                else:
                    self.logger.error(f"Waiting {wait_time} secs and re-trying...")
                    #self.logger.info(f"json: {response_raw_json}")
                    timew.sleep(wait_time)
                    retries += 1                
                
            except Exception as e:
                self.logger.error(f"Waiting {wait_time} secs and re-trying...")
                timew.sleep(wait_time)
                retries += 1

    def get_fleet_cargo_amount_request(self, fleet_name, resource_item, bearer_token):
        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        url_formated_list_fleet = self.url_get_list_fleet.format(fleet_name)
        response_raw = requests.get(url_formated_list_fleet, headers=headers)
        response_raw_json = response_raw.json()

        for fleet_item in response_raw_json:
            if fleet_item.label == fleet_name:
                for fleet_cargo in fleet_item.fleetCargo:
                    if fleet_cargo.tokenMint == resource_item:
                        return fleet_cargo.tokenAmount

        return 0
        

    def piece_function(self, input_data: InputModel):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        headers = {"Authorization": "Bearer " + client_token_loggedin['access_token']}
        self.logger.info(f"Token for {self.username_target_var} created")

        self.logger.info(f"")

        url_formated_start_mining = self.url_put_start_mining.format(input_data.fleet_name, input_data.resource_mint, input_data.planet_pk)
        self.retry_put_request(url_formated_start_mining, client_token_loggedin)
        time.sleep(10)

        self.logger.info(f"Calculate Mining Duration")
        url_formatted_fleet_mining_calculation = self.url_get_fleet_mining_calculation.format(input_data.fleet_name)
        response_fleet_mining_calculation = requests.get(url_formatted_fleet_mining_calculation, headers=headers)
        response_fleet_mining_calculation_json = response_fleet_mining_calculation.json()

        self.logger.info(f"Waiting mining for ", response_fleet_mining_calculation_json.result.timeLimit, " seconds")
        time.sleep(response_fleet_mining_calculation_json.result.timeLimit)

        url_formated_stop_mining = self.url_put_stop_mining.format(input_data.fleet_name)
        self.retry_put_request(url_formated_stop_mining, client_token_loggedin)
        time.sleep(10)

        amount_cargo = self.get_fleet_cargo_amount_request(input_data.fleet_name, input_data.resource_mint, client_token_loggedin)

        self.logger.info(f"")

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(
            fleet_name=input_data.fleet_name,
            resource_mint_mined=input_data.resource_mint,
            resource_amount_mined=amount_cargo,
        )
