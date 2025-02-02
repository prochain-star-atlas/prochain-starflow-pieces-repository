from typing import Any
from starflow.base_piece import BasePiece
from .models import InputModel, OutputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os

class StarAtlasUnloadCargoPiece(BasePiece):

    def __init__(self):

        self.server_url_var = os.environ['OPEN_ID_SERVER_URL']
        self.client_id_var = os.environ['OPEN_ID_CLIENT_ID']
        self.realm_name_var = os.environ['OPEN_ID_REALM_NAME']
        self.client_secret_var = os.environ['OPEN_ID_CLIENT_SECRET']
        self.su_username_var = os.environ['OPEN_ID_USERNAME_SERVICE_USER']
        self.su_password_var = os.environ['OPEN_ID_PASSWORD_SERVICE_USER']
        self.username_target_var = os.environ['OPEN_ID_USERNAME_TARGET']
        self.url_put_unload_cargo = os.environ['URL_PUT_UNLOAD_CARGO']
        self.url_put_unload_ammo = os.environ['URL_PUT_UNLOAD_AMMO']
        self.url_put_unload_fuel = os.environ['URL_PUT_UNLOAD_FUEL']

        self.keycloak_openid = KeycloakOpenID(server_url=self.server_url_var,
                                 client_id=self.client_id_var,
                                 realm_name=self.realm_name_var,
                                 client_secret_key=self.client_secret_var)

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

    def piece_function(self, input_data: InputModel):

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        self.logger.info(f"Token for {self.username_target_var} created")

        self.logger.info(f"")

        self.logger.info(f"Unloading Cargo for {input_data.fleet_name} on ({input_data.destination_x}, {input_data.destination_y}), {input_data.amount} {input_data.resource_mint}")
        if input_data.resource_mint == "ammoK8AkX2wnebQb35cDAZtTkvsXQbi82cGeTnUvvfK":
            url_formated_unload_ammo = self.url_put_unload_ammo.format(input_data.fleet_name, input_data.resource_mint, input_data.amount, input_data.destination_x, input_data.destination_y)
            self.retry_put_request(url_formated_unload_ammo, client_token_loggedin)
        elif input_data.resourceMint == "fueL3hBZjLLLJHiFH9cqZoozTG3XQZ53diwFPwbzNim":
            url_formated_unload_fuel = self.url_put_unload_fuel.format(input_data.fleet_name, input_data.resource_mint, input_data.amount, input_data.destination_x, input_data.destination_y)
            self.retry_put_request(url_formated_unload_fuel, client_token_loggedin)
        else:
            url_formated_unload_cargo = self.url_put_unload_cargo.format(input_data.fleet_name, input_data.resource_mint, input_data.amount, input_data.destination_x, input_data.destination_y)
            self.retry_put_request(url_formated_unload_cargo, client_token_loggedin)
        self.logger.info(f"Cargo Unloaded successfully for {input_data.fleet_name} on ({input_data.destination_x}, {input_data.destination_y}), {input_data.amount} {input_data.resource_mint}")

        self.logger.info(f"")

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(
            resource_mint_unloaded = input_data.resource_mint,
            amount_unloaded = input_data.amount,
            destination_x=input_data.destination_x,
            destination_y=input_data.destination_y,
        )
