import pytest

from sam_spot_bot_function import app
from .my_ut_config import create_env
import time

@pytest.fixture()
def init_env():
    create_env()


def test_create_bot_config(init_env):
    event = {
        "body": "{ \"name\": \"dummy_bot\", "
                " \"file_types\": \".jpg,.png\", "
                " \"bot_image\": \"bot-img.ecr.amazon.com\", "
                " \"bot_image_cmd\": \"\", "
                " \"endpoint_name\": \"autogluon-sagemaker-inference\", "
                " \"endpoint_ecr_image_path\": \"endpoint.ecr.amazon.com\", "
                " \"instance_type\": \"ml.m5.large\", "
                " \"model_s3_path\": \"\", "
                " \"create_date\": \"2020-07-27 21:39:00\", "
                " \"update_date\": \"2020-07-27 22:39:00\" }",
        "httpMethod": "POST",
    }
    ret = app.lambda_handler(event, "")
    assert ret['statusCode'] == 201


def test_update_bot_config(init_env):
    event = {
        "body": "{ \"name\": \"dummy_bot\", "
                " \"file_types\": \".jpg,.png\", "
                " \"bot_image\": \"bot-img.ecr.amazon.com\", "
                " \"bot_image_cmd\": \"\", "
                " \"endpoint_name\": \"autogluon-sagemaker-inference\", "
                " \"endpoint_ecr_image_path\": \"endpoint.ecr.amazon.com\", "
                " \"instance_type\": \"ml.m5.large\", "
                " \"model_s3_path\": \"\", "
                " \"create_date\": \"2020-07-27 21:39:00\", "
                " \"update_date\": \"2020-07-27 22:39:00\" }",
        "httpMethod": "PUT",
    }
    ret = app.lambda_handler(event, "")
    assert ret['statusCode'] == 205


def test_get_one_bot_config(init_env):
    test_create_bot_config(init_env)
    event = {
        "body": "{ \"name\": \"dummy_bot\"}",
        "httpMethod": "GET"
    }
    time.sleep(1)
    ret = app.lambda_handler(event, "")
    assert "dummy_bot" in ret["body"]


def test_delete_bot_config(init_env):
    event = {
        "body": "{ \"name\": \"dummy_bot\"}",
        "httpMethod": "DELETE"
    }
    time.sleep(1)
    ret = app.lambda_handler(event, "")
    assert ret['statusCode'] == 202
