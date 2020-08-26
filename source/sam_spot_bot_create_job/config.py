import os
from urllib.parse import urlparse
from .iam_helper import IamHelper


class PlannerConfig:
    """
    There are two way to provide the config for lambda:
        For UT to run, please go to the unit folder and change "my_ut_config.py" - and never commit that file.
        To run it on Aws, we need to modify the ENV part in template.yaml and the cfn config in the deployment folder.
    """
    esDomain = None
    esProtocol = None
    esPort = None
    sagemaker_role = None
    batch_subnets = None
    spot_fleet_role = None
    batch_instance_role = None
    batch_compute_env_sg = None
    batch_compute_type = None
    batch_bot_vCPU = 4
    batch_bot_mem = 8096
    batch_service_role = None
    sf_role_arn = None
    batch_EC2_vCPU_MIN = 8
    batch_EC2_vCPU_MAX = 128

    def __init__(self):
        # Sample ES URL- https://search-discovery-video-poc-zotdj6bsssmw4istsor56t2f2a.us-east-1.es.amazonaws.com
        url = os.getenv("ES_URL")
        url = url if url.startswith('http') else 'https://' + url  # Defaults to https
        es_parse = urlparse(url)
        print(">>> ES_URL env variable is-  " + os.getenv("ES_URL"))
        self.esProtocol = es_parse.scheme
        self.esDomain = es_parse.hostname
        if es_parse.port is None:
            self.esPort = "443" if es_parse.scheme == "https" else "80"
        else:
            self.esPort = str(es_parse.port)
        self.sagemaker_role = os.getenv("SAGEMAKER_ROLE")
        self.spot_fleet_role = os.getenv("SPOT_FLEET_ROLE")
        self.batch_instance_role = os.getenv("BATCH_INSTANCE_ROLE")
        self.batch_subnets = os.getenv("BATCH_SUBNETS")
        self.batch_compute_env_sg = os.getenv("BATCH_COMPUTE_ENV_SG")
        self.batch_compute_type = os.getenv("BATCH_COMPUTE_TYPE")
        self.batch_service_role = os.getenv("BATCH_SERVICE_ROLE")
        self.sf_role_arn = os.getenv("SF_ROLE_ARN")
        helper = IamHelper()
        self.region = helper.get_region()

        self.batch_EC2_vCPU_MIN = int(os.getenv("BATCH_EC2_VCPU_MIN", '8'))
        self.batch_EC2_vCPU_MAX = int(os.getenv("BATCH_EC2_VCPU_MAX", '128'))
        # For bot the images
        # We need to point to shared ecr images by default values - as denoted by the following default value.
        # If customer want to override they can set the environment variables in the Lambda.

        # Bot config is moved to the BotDao.

        print(">>> ENV: " + str({
            "esDomain": self.esDomain,
            'esPort': self.esPort,
            'esProtocol': self.esProtocol,  # HTTP or HTTPS
            'sf_role_arn': self.sf_role_arn,
            # AWS Batch
            'batch_compute_type': self.batch_compute_type,  # can be SPOT or EC2
            'batch_bot_vCPU': self.batch_bot_vCPU,
            'batch_bot_mem': self.batch_bot_mem,
            'batch_service_role': self.batch_service_role,
            'batch_EC2_vCPU_MAX': self.batch_EC2_vCPU_MAX,
            'batch_EC2_vCPU_MIN': self.batch_EC2_vCPU_MIN,
            'batch_subnets': self.batch_subnets,
            'batch_compute_env_sg': self.batch_compute_env_sg,
            # https://docs.aws.amazon.com/batch/latest/userguide/instance_IAM_role.html
            # Please double check it is instance arn
            'batch_instance_role': self.batch_instance_role,
            'spot_fleet_role': self.spot_fleet_role,
            'sagemaker_role': self.sagemaker_role
        }))

    @staticmethod
    def get_bot_names():
        return ["CHINESE_ID_OCR", "SENTIMENT_ANALYSIS", "CAR_ACCIDENT_INSPECTOR"]
