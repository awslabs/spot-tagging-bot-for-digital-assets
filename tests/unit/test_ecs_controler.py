import pytest

from sam_spot_bot_create_job import ecs_controller
from sam_spot_bot_create_job.ecs_controller import EcsController
from .my_ut_config import create_env


@pytest.fixture
def ecs_ctl() -> EcsController:
    create_env()
    return ecs_controller.EcsController()


def test_create_fargete_cluster(ecs_ctl):
    ecs_ctl.create_fargate_cluster()


def test_get_cluster_status(ecs_ctl):
    status = ecs_ctl.get_cluster_status()
    print(status)
    assert status != None


@pytest.mark.skip
def test_delete_cluster(ecs_ctl):
    """ pass if no exception... """
    ecs_ctl.delete_cluster()
