import json
import uuid

import boto3

from .batch_controller import BatchController
from .config import PlannerConfig
from .iam_helper import IamHelper


class StepFunctionController:
    """
    Each bot requires a sfn_controller

    How to control a Batch job -
    https://github.com/awslabs/aws-batch-helpers/blob/master/gpu-example/submit-job.py
    """

    _config = PlannerConfig()
    SFN_ROLE_ARN = _config.sf_role_arn
    SFN_NAME = "spot_bot_controller_v1"

    def __init__(self):
        """
        Create SFN if not exist.
        :param es_url:
        """
        sfn_def = {
            "Comment": "Start a Spot Bot job.",
            "StartAt": "Create aws batch job",
            "States": {
                "Create aws batch job": {
                    "Type": "Task",
                    "Resource": "arn:{}:states:::batch:submitJob.sync".format(IamHelper.get_partition()),
                    "Parameters": {
                        "JobDefinition.$": "$.JobDefinition",
                        "JobName.$": "$.JobName",
                        "JobQueue.$": "$.JobQueue",
                        "ContainerOverrides": {
                            "Vcpus": 1,
                            "Environment": [
                                {
                                    "Name": "es_port",
                                    "Value.$": "$.es_port"
                                },
                                {
                                    "Name": "es_host",
                                    "Value.$": "$.es_host"
                                },
                                {
                                    "Name": "es_index",
                                    "Value.$": "$.es_index"
                                },
                                {
                                    "Name": "es_protocol",
                                    "Value.$": "$.es_protocol"
                                },
                                {
                                    "Name": "job_id",
                                    "Value.$": "$.job_id"
                                },
                                {
                                    "Name": "batch_id",
                                    "Value.$": "$.batch_id"
                                },
                                {
                                    "Name": "output_s3_bucket",
                                    "Value.$": "$.output_s3_bucket"
                                },
                                {
                                    "Name": "output_s3_prefix",
                                    "Value.$": "$.output_s3_prefix"
                                },
                                {
                                    "Name": "endpoint_name",
                                    "Value.$": "$.endpoint_name"
                                },
                                {
                                    "Name": "region_name",
                                    "Value.$": "$.region_name"
                                }
                            ]
                        }
                    },
                    "Next": "Check job status"
                },
                "Check job status": {
                    "Type": "Pass",
                    "Result": "World",
                    "End": True
                }
            }
        }
        self.client = boto3.client("stepfunctions")
        self.sf_arn = None
        try:
            response = self.client.create_state_machine(
                name=self.SFN_NAME,
                definition=json.dumps(sfn_def),
                roleArn=self.SFN_ROLE_ARN,
                type='STANDARD',
            )

            self.sf_arn = response["stateMachineArn"]
            print(">>> sf definition {} created.".format(self.sf_arn))

        except Exception as e:
            print("!!! Cannot create Step Function - Exception is >> {}".format(e))
            if type(e).__name__ == "StateMachineAlreadyExists":
                print("Skip sf creation because it is created before.")
            else:
                raise e

        print("<<< StepFunction Controller created- " + json.dumps(sfn_def))

    def create_sf_instance(self, es_port, es_host, es_index, es_protocol, job_id,
                           output_s3_bucket, output_s3_prefix, endpoint_name, bot_id, batch_id):
        """
        Create one instance for one bot.
        Pass the bulk id.
        """
        self.batch_ctl = BatchController(bot_id=bot_id)
        batch_details = self.batch_ctl.setup_and_get_job_details_for_sf()
        jd = batch_details["jobDefinition"]
        jq = batch_details['jobQueue']
        batch_job_name = bot_id + "-with_batch_id-" + str(batch_id)

        in_para = {
            "JobName": batch_job_name,
            "JobQueue": jq,
            "JobDefinition": jd,
            "region_name": IamHelper.get_region(),
            "endpoint_name": endpoint_name,
            "output_s3_bucket": output_s3_bucket,
            "output_s3_prefix": output_s3_prefix,
            "batch_id": str(batch_id),
            "job_id": job_id,
            "es_protocol": es_protocol,
            "es_index": es_index,
            "es_host": es_host,
            "es_port": str(es_port),
        }
        sfn_instance_name = "{}-{}-{}".format(bot_id, batch_id, job_id)
        print(">>> Create SFN instance: {} with parameter {}".format(sfn_instance_name, in_para))
        self.client.start_execution(
            stateMachineArn=self.get_sf_arn(),
            name=sfn_instance_name,
            input=json.dumps(in_para)
        )
        print("bot with id {} created.".format(bot_id))

    def get_sf_arn(self):
        if self.sf_arn is not None:
            return self.sf_arn
        else:
            return "arn:{}:states:{}:{}:stateMachine:{}".format(IamHelper.get_partition(), IamHelper.get_region(),
                                                                IamHelper.get_account_id(),
                                                                self.SFN_NAME)
