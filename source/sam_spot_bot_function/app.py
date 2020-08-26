import boto3
import json
import os
from sam_spot_bot_create_job.bot_dao import BotDao

# Global variables are reused across execution contexts (if available)
session = boto3.Session()


def lambda_handler(event, context):
    """
    Sample json in API request body -
         {
            "name": name,
            "file_types": file_types,
            "bot_image": bot_image,
            "bot_image_cmd": bot_image_cmd,
            "endpoint_name": endpoint_name,
            "endpoint_ecr_image_path": endpoint_ecr_image_path,
            "instance_type": instance_type,
            "model_s3_path": model_s3_path,
            "create_date": create_date,
            "update_date": update_date
        }
    """
    print("Received event: " + json.dumps(event, indent=2))
    print("All ENV " + str(os.environ))

    method = event["httpMethod"]
    request_body = json.loads(event["body"])
    botDao = BotDao()

    if method is "POST":
        botDao.create_one_bot(**request_body)
        return {
            "statusCode": 201,
            "body": "Created"
        }
    elif method is "PUT":
        botDao.update_bot_by_name(**request_body)
        return {
            "statusCode": 205,
            "body": "Reset Content"
        }
    elif method is "DELETE":
        botDao.delete_bot_by_name(request_body["name"])
        return {
            "statusCode": 202,
            "body": "Accepted"
        }
    elif method is "GET":
        bot = botDao.get_bot_def(request_body["name"])
        return {
            "statusCode": 200,
            "body": json.dumps(bot)
        }

    return {
        "statusCode": 405,
        "body": "Method not allowed."
    }
