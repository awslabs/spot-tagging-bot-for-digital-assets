import pytest

from .my_ut_config import create_env

create_env()
from sam_spot_bot_create_job import stepfunction_controller
from sam_spot_bot_create_job.config import PlannerConfig
from sam_spot_bot_create_job.job_dao import JobDao
from sam_spot_bot_create_job.iam_helper import IamHelper
from sam_spot_bot_create_job.bot_dao import BotDao

@pytest.fixture
def sfn_ctl() -> stepfunction_controller.StepFunctionController:
    create_env()
    return stepfunction_controller.StepFunctionController()


def test_create_sf_def(sfn_ctl):
    # TODO make the arn dynamically generated.
    assert sfn_ctl.get_sf_arn() == "arn:aws:states:{}:{}:stateMachine:spot_bot_controller".format(
        IamHelper.get_region(), IamHelper.get_account_id())


def test_create_sf_instance(sfn_ctl):
    _config = PlannerConfig()
    bot_dao = BotDao()
    sfn_ctl.create_sf_instance(es_host=_config.esDomain,
                               es_port=_config.esPort,
                               es_index=JobDao.INDEX_NAME,
                               es_protocol=_config.esProtocol,
                               job_id='f0a96351-9b01-402d-9ee2-51b91a86ac5f',
                               output_s3_bucket="spot.bot.asset",
                               endpoint_name=bot_dao.get_bot_def("SENTIMENT_ANALYSIS")['endpoint_name'],
                               bot_id="SENTIMENT_ANALYSIS",
                               batch_id="2")
