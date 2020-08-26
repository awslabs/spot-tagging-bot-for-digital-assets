import time
from datetime import datetime

import boto3

from .config import PlannerConfig
from .bot_dao import BotDao


class BatchController:
    """
    The creation part will ONLY be used by StepFunction controller.
    The teardown part is not clear for now.

    Implement Ref-
    https://github.com/awslabs/aws-batch-helpers/blob/master/gpu-example/create-batch-entities.py

    Roles needed-
    https://docs.aws.amazon.com/batch/latest/userguide/spot_fleet_IAM_role.html

    Troubleshooting-
    https://docs.aws.amazon.com/zh_cn/batch/latest/userguide/troubleshooting.html#job_stuck_in_runnable

    """
    _config = PlannerConfig()
    # Shared bot spec goes here.
    COMPUTE_ENV_NAME = "spot_bot_compute"
    INSTANCE_TYPE = _config.batch_compute_type
    UNIT_V_CPU = _config.batch_bot_vCPU
    EC2_VCPU_MIN = _config.batch_EC2_vCPU_MIN
    EC2_VCPU_MAX = _config.batch_EC2_vCPU_MAX
    SERVICE_ROLE = _config.batch_service_role
    INSTANCE_ROLE = _config.batch_instance_role
    SUBNETS = _config.batch_subnets
    BOT_MEM = _config.batch_bot_mem
    BOT_CPU = _config.batch_bot_vCPU
    SPOT_FLEET_ROLE = _config.spot_fleet_role

    SECURITY_GROUPS = [_config.batch_compute_env_sg]
    REGION = boto3.session.Session().region_name
    suffix = ""
    if REGION in ("cn-north-1", "cn-northwest-1"):
        suffix = ".cn"
    END_POINT = endpoint_url = 'https://batch.' + REGION + '.amazonaws.com' + suffix
    bot_dao = BotDao()

    def __init__(self, bot_id):
        # Individual bot features goes here.
        self.bot_id = bot_id
        self.jobQueueName = self.bot_id + '_queue_' + self.COMPUTE_ENV_NAME
        self.bot_image = BatchController.bot_dao.get_bot_def(bot_name=bot_id)['bot_image']
        self.job_def = self.bot_id + "_def"
        self.bot_cmd = BatchController.bot_dao.get_bot_def(bot_name=bot_id)['bot_image_cmd']
        self.batch_client = boto3.client(
            service_name='batch',
            region_name=boto3.session.Session().region_name,
            endpoint_url=self.END_POINT)

        self.cw_client = boto3.client(
            service_name='logs',
            region_name=boto3.session.Session().region_name,
            endpoint_url=self.END_POINT)

    ####################################################################################################################
    # Setup computing basics.
    ####################################################################################################################

    def create_compute_environment(self):
        """
        Blocking method
        """
        print("Subnets is {}".format(self.SUBNETS))
        response = []
        subnet_lst = []
        for n in self.SUBNETS.split(","):
            subnet_lst.append(n)
        try:
            response = self.batch_client.create_compute_environment(
                computeEnvironmentName=self.COMPUTE_ENV_NAME,
                type='MANAGED',
                state='ENABLED',
                serviceRole=self.SERVICE_ROLE,
                computeResources={
                    'type': self.INSTANCE_TYPE,
                    "allocationStrategy": 'SPOT_CAPACITY_OPTIMIZED',
                    "bidPercentage": 100,
                    'minvCpus': self.EC2_VCPU_MIN,
                    'maxvCpus': self.EC2_VCPU_MAX,
                    'desiredvCpus': self.EC2_VCPU_MIN,
                    'instanceTypes': [
                        'optimal'
                    ],
                    'subnets': subnet_lst,
                    'securityGroupIds': self.SECURITY_GROUPS,
                    # 'ec2KeyPair': keyPair,  # not required
                    'instanceRole': self.INSTANCE_ROLE,
                    'spotIamFleetRole': self.SPOT_FLEET_ROLE
                }
            )
        except Exception as e:
            if "Object already exists" in str(e):
                print("!!! Batch Env already exists, no need to create again. ")
            else:
                print("!!! ERROR creating Batch ENV.")
                raise

        while True:
            time.sleep(1)
            describe = self.batch_client.describe_compute_environments(computeEnvironments=[self.COMPUTE_ENV_NAME])
            compute_environment = describe['computeEnvironments'][0]
            status = compute_environment['status']
            if status == 'VALID' and compute_environment['state'] == 'ENABLED':
                print('\rSuccessfully created compute environment %s' % self.COMPUTE_ENV_NAME)
                break
            elif status == 'INVALID':
                reason = compute_environment['statusReason']
                raise Exception('Failed to create compute environment: %s' % reason)
            print('\rCreating compute environment... current status is {} '.format(status))

        return response

    def create_job_queue(self):
        """
        Blocking method
        """
        response = []
        try:
            response = self.batch_client.create_job_queue(jobQueueName=self.jobQueueName,
                                                          priority=0,
                                                          computeEnvironmentOrder=[
                                                              {
                                                                  'order': 0,
                                                                  'computeEnvironment': self.COMPUTE_ENV_NAME
                                                              }
                                                          ])
        except Exception as e:
            if "Object already exists" in str(e):
                print("!!! Batch job queue already exists, no need to create again. ")
            else:
                print("!!! ERROR creating Batch job queue.")
                raise

        while True:
            time.sleep(1)
            describe = self.batch_client.describe_job_queues(jobQueues=[self.jobQueueName])
            job_queue = describe['jobQueues'][0]
            status = job_queue['status']
            if status == 'VALID':
                print('\rSuccessfully created job queue %s' % self.jobQueueName)
                break
            elif status == 'INVALID':
                reason = job_queue['statusReason']
                raise Exception('Failed to create job queue: %s' % reason)
            print('\rCreating job queue... ')

        print("<<< Created job queue: " + str(response))

        return self.jobQueueName

    def register_job_definition(self):
        response = self.batch_client.register_job_definition(jobDefinitionName=self.job_def,
                                                             type='container',
                                                             containerProperties={
                                                                 'image': self.bot_image,
                                                                 'vcpus': self.BOT_CPU,
                                                                 'memory': self.BOT_MEM,
                                                                 'privileged': True,
                                                                 # For GPU -
                                                                 # 'volumes': [
                                                                 #     {
                                                                 #         'host': {
                                                                 #             'sourcePath': '/var/lib/nvidia-docker/volumes/nvidia_driver/latest'
                                                                 #         },
                                                                 #         'name': 'nvidia-driver-dir'
                                                                 #     }
                                                                 # ],
                                                                 # 'mountPoints': [
                                                                 #     {
                                                                 #         'containerPath': '/usr/local/nvidia',
                                                                 #         'readOnly': True,
                                                                 #         'sourceVolume': 'nvidia-driver-dir'
                                                                 #     }
                                                                 # ]
                                                             })
        print('Created job definition %s' % response['jobDefinitionName'])
        return response

    def delete_job_queue(self):
        response = self.batch_client.delete_job_queue(
            jobQueue=self.jobQueueName
        )
        print("delete batch queue: " + str(response))

    def delete_compute_environment(self):

        response = self.batch_client.delete_compute_environment(
            computeEnvironment=self.COMPUTE_ENV_NAME
        )
        print("delete batch compute env: " + str(response))

    def setup_and_get_job_details_for_sf(self):
        """
        StepFunction need the name/ARN for jobDefinition, jobName, jobQueue
        """

        self.create_compute_environment()
        jq_response = self.create_job_queue()
        jd_response = self.register_job_definition()
        return dict(jobDefinition=jd_response["jobDefinitionName"], jobQueue=jq_response)

    ####################################################################################################################
    # Create runtime jobs
    ####################################################################################################################

    def submit_job(self, batch_id):
        """
        This function is for test only, in the design we will use StepFunction to submit job.
        :param batch_id:
        :return:
        """

        job_name = self.bot_id + "_" + batch_id
        job_queue = self.jobQueueName
        job_definition = self.job_def
        command = self.bot_cmd

        kwargs = {'jobName': job_name,
                  'jobQueue': job_queue,
                  'jobDefinition': job_definition,
                  'containerOverrides': {'command': [command]}}
        print(">>> Going to create job: " + str(kwargs))
        submit_job_response = self.batch_client.submit_job(jobName=job_name,
                                                           jobQueue=job_queue,
                                                           jobDefinition=job_definition,
                                                           # containerOverrides={'command': [command]}
                                                           )

        print(">>> submit job response is :" + str(submit_job_response))
        job_id = submit_job_response['jobId']
        print('Submitted job [%s - %s] to the job queue [%s]' % (job_name, job_id, job_queue))
