import time

import pytest

from sam_spot_bot_create_job.bot_dao import BotDao
from .my_ut_config import create_env


@pytest.fixture
def init_env():
    create_env()
    dao = BotDao()

    yield
    print("UT clean up.")
    time.sleep(1)
    dao.delete_index()


def test_default_bots_was_there(init_env):
    dao = BotDao()
    time.sleep(3)
    assert dao.get_bot_def("CHINESE_ID_OCR") is not None


def test_delete_index(init_env):
    dao = BotDao()
    _doc = {
        "name": "dummy_bot",
        "file_types": ".jpg,.png",
        "bot_image": "bot-img.ecr.amazon.com",
        "bot_image_cmd": "",
        "endpoint_name": "autogluon-sagemaker-inference",
        "endpoint_ecr_image_path": "endpoint.ecr.amazon.com",
        "instance_type": "ml.m5.large",
        "model_s3_path": "",
        "create_date": "2020-07-27 21:39:00",
        "update_date": "2020-07-27 22:39:00"
    }
    resp = dao.create_one_bot(**_doc)
    time.sleep(1)
    dao.delete_index()


def test_create_bot(init_env):
    dao = BotDao()

    _doc = {
        "name": "dummy_bot",
        "file_types": ".jpg,.png",
        "bot_image": "bot-img.ecr.amazon.com",
        "bot_image_cmd": "",
        "endpoint_name": "autogluon-sagemaker-inference",
        "endpoint_ecr_image_path": "endpoint.ecr.amazon.com",
        "instance_type": "ml.m5.large",
        "model_s3_path": "",
        "create_date": "2020-07-27 21:39:00",
        "update_date": "2020-07-27 22:39:00"
    }
    resp = dao.create_one_bot(**_doc)
    assert resp["_id"] is not None
    time.sleep(1)
    found = dao.get_bot_def("dummy_bot")
    assert found["name"] == "dummy_bot"


def test_update_bot_by_name(init_env):
    dao = BotDao()

    _doc = {
        "name": "dummy_bot",
        "file_types": ".jpg,.png",
        "bot_image": "bot-img.ecr.amazon.com",
        "bot_image_cmd": "",
        "endpoint_name": "autogluon-sagemaker-inference",
        "endpoint_ecr_image_path": "endpoint.ecr.amazon.com",
        "instance_type": "ml.m5.large",
        "model_s3_path": "",
        "create_date": "2020-07-27 21:39:00",
        "update_date": "2020-07-27 22:39:00"
    }
    resp = dao.create_one_bot(**_doc)
    assert resp["_id"] is not None

    _doc2 = {
        "name": "dummy_bot",
        "file_types": ".jpg2,.png2",
        "bot_image": "bot-img.ecr.amazon.com.cn",
        "bot_image_cmd": "",
        "endpoint_name": "autogluon-sagemaker-inference",
        "endpoint_ecr_image_path": "endpoint.ecr.amazon.com",
        "instance_type": "ml.m5.large",
        "model_s3_path": "",
        "create_date": "2020-07-27 21:39:00",
        "update_date": "2020-07-27 22:39:00"
    }
    time.sleep(2)  # Due to final constancy.
    assert dao.update_bot_by_name(**_doc2) > 0

    time.sleep(2)
    found = dao.get_bot_def("dummy_bot")
    assert found["bot_image"].endswith(".cn") is True


def test_delete_bot_by_name(init_env):
    dao = BotDao()

    _doc = {
        "name": "dummy_bot",
        "file_types": ".jpg,.png",
        "bot_image": "bot-img.ecr.amazon.com",
        "bot_image_cmd": "",
        "endpoint_name": "autogluon-sagemaker-inference",
        "endpoint_ecr_image_path": "endpoint.ecr.amazon.com",
        "instance_type": "ml.m5.large",
        "model_s3_path": "",
        "create_date": "2020-07-27 21:39:00",
        "update_date": "2020-07-27 22:39:00"
    }
    resp = dao.create_one_bot(**_doc)
    assert resp["_id"] is not None

    time.sleep(2)  # Due to final constancy.
    ret = dao.delete_bot_by_name("dummy_bot")
    assert ret['deleted'] == 1
