import os

import pytest

from sam_spot_bot_create_job.config import PlannerConfig
from .my_ut_config import create_env


@pytest.fixture()
def ut_env():
    """ Generates API GW Event"""
    create_env()
    return None


def test_check_env_received(ut_env):
    ut_config = PlannerConfig()
    assert os.getenv("ES_URL") is not None
    assert ut_config.esProtocol is not None
    assert ut_config.spot_fleet_role is not None
    assert ut_config.esDomain is not None
