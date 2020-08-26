import json

import boto3


class IamHelper:

    def __init__(self):
        self.client = boto3.client("iam")
        self.ssm_client = boto3.client('ssm')

    def create_or_get_ecs_role(self) -> str:
        self.role_name = "spot-bot-ecs-service-role"

        print("Check role exist")
        try:
            response = self.client.get_role(
                RoleName=self.role_name,
            )
            print("<<< Role exist and role ARN is " + response["Role"]["Arn"])
            return response["Role"]["Arn"]
        except Exception as e:
            print(type(e).__name__)  # NoSuchEntityException for the first time call.
            if type(e).__name__ == "NoSuchEntityException":
                return self._create_ecs_role()

    def _create_ecs_role(self) -> str:
        assume_role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        })

        response = self.client.create_role(
            RoleName=self.role_name,
            AssumeRolePolicyDocument=assume_role_policy_document
        )
        print("<<< created ecs role: " + str(response))
        return response["Role"]["Arn"]

    @staticmethod
    def get_account_id():
        return boto3.client('sts').get_caller_identity().get('Account')

    @staticmethod
    def get_region():
        region_name = boto3.session.Session().region_name
        print("Current Region is - ", region_name)
        return region_name

    @staticmethod
    def get_partition():
        """
        Auto switch the region partition for arn.
        """
        if boto3.session.Session().region_name in ("cn-northwest-1", "cn-north-1"):
            print("China region")
            return "aws-cn"
        else:
            return "aws"

