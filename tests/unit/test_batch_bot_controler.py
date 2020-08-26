import time

import pytest

from .my_ut_config import create_env

# Inject Env here otherwise the following BatchController will fail.
create_env()
from sam_spot_bot_create_job.batch_controller import BatchController


@pytest.fixture
def batch_ctl() -> BatchController:
    return BatchController("CAR_ACCIDENT_INSPECTOR")


def test_create_compute_environment(batch_ctl):
    batch_ctl.create_compute_environment()


def test_create_job_queue(batch_ctl):
    batch_ctl.create_job_queue()


def test_register_job_definition(batch_ctl):
    batch_ctl.register_job_definition()


def test_submit_job(batch_ctl):
    batch_ctl.submit_job("unit_test_batch_id_" + str(int(round(time.time() * 1000))))


@pytest.mark.skip
def test_delete_job_queue(batch_ctl):
    batch_ctl.delete_job_queue()


@pytest.mark.skip
def test_delete_compute_environment(batch_ctl):
    batch_ctl.delete_compute_environment()
