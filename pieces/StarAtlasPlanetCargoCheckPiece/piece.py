from typing import Any
from starflow.base_piece import BasePiece, BaseBranchOutputModel
from .models import InputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import json

class StarAtlasPlanetCargoCheckPiece(BasePiece):

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
        self.url_get_cargo_by_starbase = self.read_secrets('URL_GET_CARGO_BY_STARBASE')
        self.url_get_starbase_by_coords = self.read_secrets('URL_GET_STARBASE_BY_COORDS')

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

    def get_planet_cargo_for_mint(self, starbase_pk, resource_mint, bearer_token):

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        url_formated_list_cargo = self.url_get_cargo_by_starbase.format(starbase_pk)
        response_raw = requests.get(url_formated_list_cargo, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        resource_amount = 0

        for planet_cargo_item in response_raw_json:
            if planet_cargo_item["tokenMint"] == resource_mint:
                resource_amount = planet_cargo_item["tokenAmount"]

        return resource_amount

    def get_planet_pk_by_coords(self, x, y):

        url_formated_get_starbase_pk = self.url_get_starbase_by_coords.format(x, y)
        response_raw = requests.get(url_formated_get_starbase_pk, verify=False)
        response_raw_json = response_raw.json()

        return response_raw_json[0]["starbase"]["starbasePK"]

    def piece_function(self, input_data: InputModel, workspace_id):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        self.logger.info(f"Token for {self.username_target_var} created")

        self.logger.info(f"")

        starbase_pk = self.get_planet_pk_by_coords(input_data.location_x, input_data.location_y)

        cargo_planet_amount = self.get_planet_cargo_for_mint(starbase_pk, input_data.resource_mint, bearer_token=client_token_loggedin)

        test_check_res = cargo_planet_amount >= input_data.resource_amount
            
        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return BaseBranchOutputModel(
            branch_main=test_check_res
        )
