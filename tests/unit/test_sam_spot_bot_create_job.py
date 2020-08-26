import pytest

from .my_ut_config import create_env

create_env()
from sam_spot_bot_create_job import app
from sam_spot_bot_create_job.job_dao import JobDao
import os
from sam_spot_bot_create_job.sagemaker_controller import SageMakerController
import uuid

BOT_NAME = "CHINESE_ID_OCR"


@pytest.fixture()
def event():
    create_env()
    es_dao = JobDao()
    es_dao.delete_index()

    yield  # the code below yield is used to clean up.

    print("<<< UT Cleanup...")
    os.environ["BOT_UT"] = "FALSE"

    # sm_ctl = SageMakerController()
    # sm_ctl.delete_endpoint()
    print("<<< UT Cleanup end...")


def test_lambda_handler(event):
    """ Generates API GW Event"""
    e = {"s3_bucket": "bot-ocr-test-bucket",
         "s3_path": "",
         "bot_name": BOT_NAME,
         "bulk_size": "500",
         "number_of_bots": "1",
         "output_s3_bucket": "bot-ocr-test-bucket",
         "job_id": str(uuid.uuid4())}

    ret = app.lambda_handler(e, "")
    assert ret['statusCode'] == 201
