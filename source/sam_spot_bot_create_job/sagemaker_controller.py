# -*- coding: utf-8 -*-
# @Time    : 6/19/20 3:28 PM
# @Author  : Jackie
# @File    : EndpointDeploy.py
# @Software: PyCharm

import boto3
import time

from .config import PlannerConfig
from .bot_dao import BotDao
from .stepfunction_controller import StepFunctionController


class SageMakerController:

    def __init__(self, bot_id):
        """
        """
        self.bot_name = bot_id
        self._config = PlannerConfig()
        self.bot_dao = BotDao()
        bot_def = self.bot_dao.get_bot_def(self.bot_name)
        self.endpoint_ecr_image_path = bot_def['endpoint_ecr_image_path']
        if bot_def["model_s3_path"] != "":
            self.model_file = True
            self.model_s3_path = bot_def["model_s3_path"]
        else:
            self.model_file = False
        self.instance_type = bot_def["instance_type"]
        self.endpoint_name = bot_def["endpoint_name"]

    def deploy(self):
        if len(self.endpoint_name.split(',')) > 1:
            self.multi_endpoint_deploy_sync()
        else:
            self.deploy_sync(self.endpoint_name, self.endpoint_ecr_image_path, self.instance_type, self.model_s3_path)
            self.periodically_check(self.endpoint_name)

    def multi_endpoint_deploy_sync(self):
        endpoint_name_list = self.endpoint_name.split(",")
        ecr_image_path_list = self.endpoint_ecr_image_path.split(",")
        model_s3_path_list = self.model_s3_path.split(",")
        # assert two list length the same
        print("endpoint length: ", len(endpoint_name_list))
        print("endpoint ecr length: ", len(ecr_image_path_list))
        if len(endpoint_name_list) != len(ecr_image_path_list):
            raise AssertionError
        endpoint_number = len(endpoint_name_list)
        for i in range(endpoint_number):
            self.deploy_sync(endpoint_name_list[i], ecr_image_path_list[i], self.instance_type, model_s3_path_list[i])

        for i in range(endpoint_number):
            self.periodically_check(endpoint_name_list[i])
        return None

    def deploy_sync(self, endpoint_name, endpoint_ecr_image_path, instance_type, model_s3_path):
        if self.is_endpoint_running(endpoint_name) is not None:
            print("Endpoint already exist and will return.")
            return

        try:
            global role
            print("Using fixed role.")
            role = self._config.sagemaker_role
        except Exception as e:
            print("SageMaker Role doesn't exist.")
        try:
            sm = boto3.Session().client('sagemaker')
            if self.model_file is True:
                primary_container = {'Image': endpoint_ecr_image_path, 'ModelDataUrl': model_s3_path}
            else:
                primary_container = {'Image': endpoint_ecr_image_path}

            print("model_name: ", endpoint_name)
            print("endpoint_ecr_image_path: ", endpoint_ecr_image_path)
            create_model_response = sm.create_model(ModelName=endpoint_name,
                                                    ExecutionRoleArn=role,
                                                    PrimaryContainer=primary_container)

            # create endpoint config
            endpoint_config_name = endpoint_name + '-config'
            create_endpoint_config_response = sm.create_endpoint_config(EndpointConfigName=endpoint_config_name,
                                                                        ProductionVariants=[{
                                                                            'InstanceType': instance_type,
                                                                            'InitialVariantWeight': 1,
                                                                            'InitialInstanceCount': 1,
                                                                            'ModelName': endpoint_name,
                                                                            'VariantName': 'AllTraffic'}])

            # create endpoint
            create_endpoint_response = sm.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name)

        except Exception as e:
            print("!!! Cannot create endpoint - Exception is >> {}".format(e))
            if type(e).__name__ == "StateMachineAlreadyExists":
                print("Skip sf creation because it is created before.")
            else:
                raise e

        print("<<< Completed model endpoint deployment. " + str(endpoint_name))

    def delete_endpoint(self, endpoint_name):
        print(">>> About to delete endpoint: " + endpoint_name)
        client = boto3.client('sagemaker')
        endpoint_config_name = endpoint_name + '-config'
        response = client.describe_endpoint_config(EndpointConfigName=endpoint_config_name)
        model_name = response['ProductionVariants'][0]['ModelName']
        try:
            print(">>> Going to delete model: " + model_name)
            client.delete_model(ModelName=model_name)
        except Exception as e:
            print("having trouble to remove model. will continue to clean up endpoint." + type(e).__name__)
        try:
            print(">>> Going to delete endpoint: " + endpoint_name)
            client.delete_endpoint(EndpointName=endpoint_name)
        except Exception as e:
            print("having trouble to remove endpoint. will continue to clean up endpoint config." + type(e).__name__)
        try:
            print(">>> Going to delete endpoint config: " + endpoint_config_name)
            client.delete_endpoint_config(EndpointConfigName=endpoint_config_name)
        except Exception as e:
            print("having trouble to remove endpoint config. " + type(e).__name__)

    def is_endpoint_running(self, endpoint_name):
        """
        Content of check_name could be "InService" or other.
        if the named endpoint doesn't exist then return None.
        """
        client = boto3.client('sagemaker')
        endpoints = client.list_endpoints()
        endpoint_name_list = [(ep["EndpointName"], ep["EndpointStatus"]) for ep in endpoints["Endpoints"]]
        for check_name in endpoint_name_list:
            if endpoint_name == check_name[0]:
                return check_name[1]
        return None

    def periodically_check(self, endpoint_name) -> bool:
        count = 0
        while True:
            status = self.is_endpoint_running(endpoint_name)
            if status == "InService":
                return True
            else:
                count += 1
                print("Checking endpoint {} - {}/120".format(endpoint_name, count))
                if count > 120:
                    return False

                time.sleep(10)

    def bot_cleanup(self):
        print('>>> start to cleanup bot:', self.bot_name)

        _config = PlannerConfig()  # Allow dynamically update config for each task.

        # check if input bot name is a valid one
        if self.bot_name not in _config.get_bot_names():
            raise Exception("Bot name is not allowed.")

        # check status of currently sf executions
        SFN_NAME = StepFunctionController.SFN_NAME
        try:
            client = boto3.client('stepfunctions')

            response = client.list_state_machines()
            stms = response['stateMachines']
            stm = None
            for _stm in stms:
                if _stm['name'] == SFN_NAME:
                    stm = _stm

            if stm is None:
                err = {'msg': 'bot state machine not found'}
                raise Exception(err)

            sf_arn = stm['stateMachineArn']
            response = client.list_executions(stateMachineArn=sf_arn)
        except Exception as e:
            print("!!! Cannot list executions for state machine:{} - Exception is >> {}".format(sf_arn, e))
            print("Abort cleanup process")
            err = {'msg': 'Cannot list executions for state machine'}
            raise Exception(err)

        executions = response['executions']
        runnings = []
        for _exec in executions:
            if _exec['status'] == 'RUNNING':
                runnings.append(_exec)

        run_count = len(runnings)
        if run_count:
            print("{} executions remain in RUNNING status, Abort cleanup process".format(run_count))
            errmsg = "{} executions remain in RUNNING status, Abort cleanup process".format(run_count)
            raise Exception(errmsg)

        # kickoff real endpoint delete process
        try:
            endpoint_name_list = self.bot_dao.get_bot_def(self.bot_name)['endpoint_name'].split(',')
            for endpoint_name in endpoint_name_list:
                self.delete_endpoint(endpoint_name)
        except Exception as e:
            print('Failed to cleanup sagemaker endpoint with Exception:', e)
            err = {'msg': 'Failed to cleanup sagemaker endpoint'}
            raise Exception(err)

        print("Bot endpoint cleanup successfully")
