import pytest

from sam_spot_bot_create_job import iam_helper
from .my_ut_config import create_env


@pytest.fixture()
def init_env():
    """ Generates API GW Event"""
    create_env()
    return {}


def test_get_location(init_env):
    helper = iam_helper.IamHelper()
    print(helper.get_region())


def test_create_ecs_role(init_env):
    helper = iam_helper.IamHelper()
    helper.create_or_get_ecs_role()


def test_iam_helper(init_env):
    helper = iam_helper.IamHelper()
    partition = helper.get_partition()
    assert partition == "aws"
