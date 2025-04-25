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
    
    def get_planet_cargo_list(self, starbase_pk, bearer_token):

        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        url_formated_list_cargo = self.url_get_cargo_by_starbase.format(starbase_pk)
        response_raw = requests.get(url_formated_list_cargo, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        return response_raw_json

    def get_planet_pk_by_coords(self, x, y):

        url_formated_get_starbase_pk = self.url_get_starbase_by_coords.format(x, y)
        response_raw = requests.get(url_formated_get_starbase_pk, verify=False)
        response_raw_json = response_raw.json()

        return response_raw_json[0]["starbase"]["starbasePK"]

    def get_recipe_pk_for_resource_mint_output(self, resource_mint):

        response_raw = requests.get(self.url_get_recepe_list, verify=False)
        response_raw_json = response_raw.json()

        craft_recipe_pk = ""

        for cr in response_raw_json["craft"]:

            if cr["output"]["mint"] == resource_mint:
                craft_recipe_pk = cr["publicKey"]

        return craft_recipe_pk
    
    def get_recipe_obj_for_resource_mint_output(self, resource_mint):

        response_raw = requests.get(self.url_get_recepe_list, verify=False)
        response_raw_json = response_raw.json()

        craft_recipe_pk = None

        for cr in response_raw_json["craft"]:

            if cr["output"]["mint"] == resource_mint:
                craft_recipe_pk = cr

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

    def do_craft(self, x, y, resource_mint, resource_amount, crew_allocation, su_token_loggedin, client_token_loggedin):

        self.logger.info(f"Start crafting: {resource_mint}")

        url_formated_craft_main = self.url_put_start_crafting.format(x, y, resource_mint, resource_amount, crew_allocation)
        res_action_start_craft = retry_put_request(url_formated_craft_main, client_token_loggedin)

        if not(res_action_start_craft):
            raise Exception("Crafting Start Error")
        
        craft_recipe_pk = self.get_recipe_pk_for_resource_mint_output(resource_mint)

        wait_seconds_for_craft = self.get_remaining_time_for_recipe_craft(x, y, craft_recipe_pk, bearer_token=client_token_loggedin)

        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)

        self.logger.info(f"Wait craft to finish: {wait_seconds_for_craft} seconds")
        sleep(wait_seconds_for_craft)  

        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)

        craft_id = self.get_crafting_id_recipe_craft(x, y, craft_recipe_pk, bearer_token=client_token_loggedin)

        self.logger.info(f"End crafting: {craft_id}")

        url_formated_end_craft_main = self.url_put_end_crafting.format(x, y, craft_id)
        res_action_start_craft = retry_put_request(url_formated_end_craft_main, client_token_loggedin)

        self.logger.info(f"Crafting finished !")

    def enough_cargo_for_craft(self, planet_cargo_list, resource_mint, resource_amount):

        test_enough_cargo = False

        for cargo_it in planet_cargo_list:
            if cargo_it["tokenMint"] == resource_mint:
                test_enough_cargo = cargo_it["tokenAmount"] >= resource_amount

        return test_enough_cargo

    def process_craft_hierarchy(self, x, y, resource_mint, resource_amount, crew_allocation, planet_cargo_list, su_token_loggedin, client_token_loggedin):

        craft_recipe_pk = self.get_recipe_obj_for_resource_mint_output(resource_mint)

        if craft_recipe_pk is None: 
            is_enough_resource_input = self.enough_cargo_for_craft(planet_cargo_list, resource_mint, resource_amount)
            return is_enough_resource_input
        
        output_amount = craft_recipe_pk["output"]["amount"]

        for input_rec in craft_recipe_pk["input"]:

            amount_required = (input_rec["amount"] / output_amount) * resource_amount
            is_enough_resource_input = self.enough_cargo_for_craft(planet_cargo_list, input_rec["mint"], amount_required)

            if is_enough_resource_input is False:
                pch = self.process_craft_hierarchy(x, y, resource_mint, resource_amount, crew_allocation, planet_cargo_list, su_token_loggedin, client_token_loggedin)
                if pch is False:
                    raise Exception("Missing resource to handle craft") 
            else:
                self.logger.info(f"Enough {resource_mint} to continue")

        is_enough_resource_output = self.enough_cargo_for_craft(planet_cargo_list, resource_mint, resource_amount)

        if is_enough_resource_output is False:
            self.do_craft(x, y, resource_mint, resource_amount, crew_allocation, su_token_loggedin, client_token_loggedin)       

        return True

    def piece_function(self, input_data: InputModel):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        self.logger.info(f"Token for {self.username_target_var} created")

        self.logger.info(f"")       

        starbase_pk = self.get_planet_pk_by_coords(input_data.destination_x, input_data.destination_y)
        planet_cargo_list = self.get_planet_cargo_list(starbase_pk, bearer_token=client_token_loggedin)

        if input_data.recursive_craft is True:          
            self.process_craft_hierarchy(input_data.destination_x, input_data.destination_y, input_data.resource_mint_to_craft, input_data.resource_amount_to_craft, input_data.crew_allocation_to_craft, planet_cargo_list, su_token_loggedin, client_token_loggedin)
        else:
            self.do_craft(input_data.destination_x, input_data.destination_y, input_data.resource_mint_to_craft, input_data.resource_amount_to_craft, input_data.crew_allocation_to_craft, su_token_loggedin, client_token_loggedin)
        
        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return OutputModel(
            resource_mint_crafted=input_data.resource_mint_to_craft,
            resource_amount_crafted=input_data.resource_amount_to_craft
        )
