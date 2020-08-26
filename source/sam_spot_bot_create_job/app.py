import json
import os
from multiprocessing import Process

import boto3

from .config import PlannerConfig
from .job_dao import JobDao
from .iam_helper import IamHelper
from .s_three_dao import SimpleStorageServiceDao
from .sagemaker_controller import SageMakerController
from .stepfunction_controller import StepFunctionController
from .bot_dao import BotDao

# Global variables are reused across execution contexts (if available)
session = boto3.Session()
_config = None


def lambda_handler(event, context):
    """
        AWS Lambda handler
            api-gateway-simple-proxy-for-lambda-output-format
            https: // docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
        
    """

    print("Received event: " + json.dumps(event, indent=2))
    print("All ENV " + str(os.environ))
    global _config
    _config = PlannerConfig()  # Allow dynamically update config for each task.
    global bot_dao
    bot_dao = BotDao()
    # Read the request parameter.
    httpMethod = event['httpMethod']
    bot_name = event["bot_name"]
    bulk_size = event["bulk_size"]
    number_of_bots = event["number_of_bots"]
    s3_bucket = event["s3_bucket"]
    s3_path = event["s3_path"]
    output_s3_bucket = event["output_s3_bucket"]
    output_s3_prefix = event['output_s3_prefix']
    job_id = event["job_id"]

    if httpMethod == "POST":
        processing(job_id, bot_name, s3_bucket, s3_path, number_of_bots, output_s3_bucket, output_s3_prefix)
    elif httpMethod == "DELETE":
        delete(bot_name)

    return respond(None, "")  # respond 201 created.

    # The following is sample code for Get and Post.
    # operation = event['httpMethod']
    # if operation in operations:
    #     payload = event['queryStringParameters'] if operation == 'GET' else json.loads(event['body'])
    #     return respond(None, operations[operation](dynamo, payload))
    # else:
    #     return respond(ValueError('Unsupported method "{}"'.format(operation)))


def respond(err, res=None):
    return {
        'statusCode': 400 if err else 201,
        'body': err["msg"] if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def processing(job_id, bot_name, s3_bucket, s3_path, number_of_bots, output_s3_bucket=None,output_s3_prefix=None):
    """
    File list are sliced to batches according to the number_of_bots. If there number_of_bots is 5, then the batch_id is
    1 to 5.
    """
    print('>>> start to work.')
    # Prepare the file list to work for.
    if bot_name not in _config.get_bot_names():
        err = {"msg": "not bot found with the name " + bot_name}
        return respond(err)

    process = start_process_async(create_endpoint, bot_name)

    s3_dao = SimpleStorageServiceDao(s3_bucket=s3_bucket, s3_path=s3_path,
                                     file_types=bot_dao.get_bot_def(bot_name)["file_types"])
    file_to_process = s3_dao.get_file_list()
    es_dao = JobDao()
    number_of_bots = int(number_of_bots)
    es_dao.save_file_list(bucket=s3_bucket, file_list=file_to_process, job_id=job_id, number_of_bots=number_of_bots),

    print(">>> Wait for endpoint creation complete.")
    process.join()  # Must wait for the endpoint creation complete.
    print("===== Endpoint created - Continue... =====")
    iam_helper = IamHelper()

    # Call bot to work on the items.
    # Every ONE step function instance represents one bot.
    for b in range(int(number_of_bots)):
        batch_id = b + 1  # batch_id started from 1 instead of 0
        # Tell bot batch ID, ES address
        sf_ctl = StepFunctionController()
        print(">>> Creating bot- {}".format(batch_id))
        sf_ctl.create_sf_instance(es_host=_config.esDomain,
                                  es_port=_config.esPort,
                                  es_index=JobDao.INDEX_NAME,
                                  es_protocol=_config.esProtocol,
                                  job_id=job_id,
                                  output_s3_bucket=output_s3_bucket,
                                  output_s3_prefix=output_s3_prefix,
                                  endpoint_name=bot_dao.get_bot_def(bot_name)['endpoint_name'],
                                  bot_id=bot_name,
                                  batch_id=batch_id)

    print("<<< SUCCESSFULLY created StepFunctions.")


def start_process_async(fn, bot_id) -> Process:
    """
    To avoid this method blocking the s3 clawer we need to execute it on another process.
    """
    bot_ut = os.getenv("BOT_UT")  # In unit test we use a different url because the relative path is not the same.
    print(">>> Start process async. In UT? {}".format(bot_ut))
    p = Process(target=fn, args=(bot_id, bot_ut,))
    p.start()
    return p


def create_endpoint(bot_id, bot_ut):
    print(">>> Start creating endpoint.")
    sm_ctl = SageMakerController(bot_id)
    sm_ctl.deploy()


    print("<<<< Completed create endpoint.")


def delete(bot_name):
    print(">>> Start to clean up the bot- " + bot_name)
    sm_ctl = SageMakerController(bot_id=bot_name)
    sm_ctl.bot_cleanup()
    print("<<< End of clean up the bot- " + bot_name)

