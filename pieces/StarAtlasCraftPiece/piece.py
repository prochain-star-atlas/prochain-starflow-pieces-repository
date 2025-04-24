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

class StarAtlasCraftPiece(BasePiece):

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
        self.url_get_list_fleet = self.read_secrets('URL_GET_LIST_FLEET')
        self.url_put_start_crafting = self.read_secrets('URL_PUT_START_CRAFTING')
        self.url_put_end_crafting = self.read_secrets('URL_PUT_END_CRAFTING')
        self.url_put_stop_crafting = self.read_secrets('URL_PUT_STOP_CRAFTING')
        self.url_get_crew_stats = self.read_secrets('URL_GET_CREW_STATS')
        self.url_get_recepe_list = self.read_secrets('URL_GET_CRAFT_RECIPE_LIST')
        self.url_get_craft_process = self.read_secrets('URL_GET_CRAFT_PROCESS')

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

    def get_recipe_pk_for_resource_mint_output(self, resource_mint):

        response_raw = requests.get(self.url_get_recepe_list, verify=False)
        response_raw_json = response_raw.json()

        craft_recipe_pk = ""

        for cr in response_raw_json["craft"]:

            if cr["output"]["mint"] == resource_mint:
                craft_recipe_pk = cr["publicKey"]

        return craft_recipe_pk
    
    def get_remaining_time_for_recipe_craft(self, x, y, craft_recipe_pk, bearer_token):

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        url_formated_craft_process = self.url_get_craft_process.format(x, y)

        response_raw = requests.get(url_formated_craft_process, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        diff_seconds_remaining = 0

        for pcp in response_raw_json["progressCraftingProcesses"]:

            if pcp["recipe"] == craft_recipe_pk:

                end_time = pcp["labelTime"]
                t = datetime.time.fromisoformat(end_time)
                ct = datetime.now(timezone.utc)
                diff_seconds_remaining = (ct-t).total_seconds()

        return diff_seconds_remaining
    
    def get_crafting_id_recipe_craft(self, x, y, craft_recipe_pk, bearer_token):

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        url_formated_craft_process = self.url_get_craft_process.format(x, y)

        response_raw = requests.get(url_formated_craft_process, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        crafting_id = 0

        for pcp in response_raw_json["progressCraftingProcesses"]:

            if pcp["recipe"] == craft_recipe_pk:

                crafting_id = pcp["craftingId"]

        return crafting_id

    def piece_function(self, input_data: InputModel):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        self.logger.info(f"Token for {self.username_target_var} created")

        self.logger.info(f"")       

        self.logger.info(f"Start crafting: {input_data.resource_mint_to_craft}")

        url_formated_craft_main = self.url_put_start_crafting.format(input_data.destination_x, input_data.destination_y, input_data.resource_mint_to_craft, input_data.resource_amount_to_craft, input_data.crew_allocation_to_craft)
        res_action_start_craft = retry_put_request(url_formated_craft_main, client_token_loggedin)

        if not(res_action_start_craft):
            raise Exception("Crafting Start Error")
        
        craft_recipe_pk = self.get_recipe_pk_for_resource_mint_output(input_data.resource_mint_to_craft)

        wait_seconds_for_craft = self.get_remaining_time_for_recipe_craft(input_data.destination_x, input_data.destination_y, craft_recipe_pk, bearer_token=client_token_loggedin)

        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)

        self.logger.info(f"Wait craft to finish: {wait_seconds_for_craft} seconds")
        sleep(wait_seconds_for_craft)  

        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)

        craft_id = self.get_crafting_id_recipe_craft(input_data.destination_x, input_data.destination_y, craft_recipe_pk, bearer_token=client_token_loggedin)

        self.logger.info(f"End crafting: {craft_id}")

        url_formated_end_craft_main = self.url_put_end_crafting.format(input_data.destination_x, input_data.destination_y, craft_id)
        res_action_start_craft = retry_put_request(url_formated_end_craft_main, client_token_loggedin)

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(
            resource_mint_crafted=input_data.resource_mint_to_craft,
            resource_amount_crafted=input_data.resource_amount_to_craft
        )
