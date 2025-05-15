from datetime import datetime, timezone
from typing import Any
from .common_utils import retry_put_request
from starflow.base_piece import BasePiece
from .models import InputModel, OutputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import json

class ReadVariablePiece(BasePiece):

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
        self.url_get_read_variable = self.read_secrets('URL_GET_READ_VARIABLE')
        self.url_put_save_variable = self.read_secrets('URL_PUT_SAVE_VARIABLE')

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

    def piece_function(self, input_data: InputModel):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        self.logger.info(f"Token for {self.username_target_var} created")

        headers = {"Authorization": "Bearer " + client_token_loggedin['access_token']}

        url_get_read_variable_key = self.url_get_read_variable.format(input_data.key)
        response_raw = requests.get(url_get_read_variable_key, headers=headers, verify=False)
        response_raw_json = response_raw.json()
            
        var_str = response_raw_json["valueString"]
        var_int = response_raw_json["valueInteger"]
        var_float = response_raw_json["valueFloat"]
        
        self.logger.info(f"Variable Read successfully for {input_data.key} on ({var_str}, {var_int}), {var_float}")

        self.logger.info(f"")

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(
            str_value=var_str,
            int_value=var_int,
            float_value=var_float
        )
