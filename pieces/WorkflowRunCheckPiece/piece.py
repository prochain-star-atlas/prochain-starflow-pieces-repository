from typing import Any
from starflow.base_piece import BasePiece, BaseBranchOutputModel
from .common_utils import retry_put_request
from .models import FleetStatusEnum, InputModel
from time import sleep
import time as timew
import requests
from keycloak import KeycloakOpenID
import os
import json

class WorkflowRunCheckPiece(BasePiece):

    def read_secrets(self, var_name):
        with open("/var/mount_secrets/" + var_name) as f:
            file_content = f.read()
            return file_content

    def init_piece(self):

        self.server_url_var = self.read_secrets('OPEN_ID_SERVER_URL')
        self.client_id_var = self.read_secrets('OPEN_ID_STARFLOW_CLIENT_ID')
        self.realm_name_var = self.read_secrets('OPEN_ID_REALM_NAME')
        self.client_secret_var = self.read_secrets('OPEN_ID_STARFLOW_CLIENT_SECRET')
        self.su_username_var = self.read_secrets('OPEN_ID_USERNAME_SERVICE_USER')
        self.su_password_var = self.read_secrets('OPEN_ID_PASSWORD_SERVICE_USER')
        self.username_target_var = os.environ['OPEN_ID_USERNAME_TARGET']
        self.url_post_start_workflow = self.read_secrets('URL_POST_START_WORKFLOW')
        self.url_post_pause_workflow = self.read_secrets('URL_POST_PAUSE_WORKFLOW')
        self.url_get_worflows = self.read_secrets('URL_GET_WORKFLOW')

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
        
    def get_workflow_is_paused(self, workflow_name, workspace_id, bearer_token):
        headers = {"Authorization": "Bearer " + bearer_token['access_token']}

        url_formated_list_workflow = self.url_get_worflows.format(workspace_id)
        response_raw = requests.get(url_formated_list_workflow, headers=headers, verify=False)
        response_raw_json = response_raw.json()

        work_is_paused = False
        for ac in response_raw_json["data"]:
            if ac["name"] == workflow_name:
                work_is_paused = ac["is_active"]

        return work_is_paused
        
    def piece_function(self, input_data: InputModel, workspace_id):

        self.init_piece()

        self.logger.info(f"Create token for {self.username_target_var}")
        su_token_loggedin = self.openid_get_token()
        client_token_loggedin = self.openid_impersonate_user_token_keycloak(su_token_loggedin)
        headers = {"Authorization": "Bearer " + client_token_loggedin['access_token']}
        self.logger.info(f"Token for {self.username_target_var} created")

        work_is_paused = self.get_workflow_is_paused(workflow_name=input_data.workflow_name, workspace_id=workspace_id, bearer_token=client_token_loggedin)

        self.logger.info(f"Logout {self.username_target_var}")
        self.openid_logout_user(client_token_loggedin)
        self.openid_logout_user(su_token_loggedin)
        self.logger.info(f"{self.username_target_var} logged out")

        # Return output
        return BaseBranchOutputModel(
            branch_main=not (work_is_paused == True)
        )