import pytest

from sam_spot_bot_create_job.bot_dao import BotDao
from sam_spot_bot_create_job.sagemaker_controller import SageMakerController
from .my_ut_config import create_env

# BOT_NAME="CHINESE_ID_OCR"
# BOT_NAME="CAR_ACCIDENT_INSPECTOR"
BOT_NAME = "SENTIMENT_ANALYSIS"


@pytest.fixture
def init_env():
    create_env()


def test_deploy(init_env):
    sm_ctl = SageMakerController(BOT_NAME)
    sm_ctl.deploy()


def test_endpoint_is_running(init_env):
    sm_ctl = SageMakerController(BOT_NAME)
    bot_dao = BotDao()
    endpoint_name_list = bot_dao.get_bot_def(BOT_NAME)['endpoint_name'].split(',')
    for endpoint_name in endpoint_name_list:
        sm_ctl.periodically_check(endpoint_name)


def test_delete_endpoint(init_env):
    sm_ctl = SageMakerController(BOT_NAME)
    bot_dao = BotDao()
    endpoint_name_list = bot_dao.get_bot_def(BOT_NAME)['endpoint_name'].split(',')
    for endpoint_name in endpoint_name_list:
        sm_ctl.delete_endpoint(endpoint_name)


def test_endpoint_not_running(init_env):
    sm_ctl = SageMakerController("BOT_NAME")
    bot_dao = BotDao()
    endpoint_name_list = bot_dao.get_bot_def(BOT_NAME)['endpoint_name'].split(',')
    for endpoint_name in endpoint_name_list:
        is_exit = sm_ctl.is_endpoint_running(endpoint_name)
        assert is_exit is None
