import pytest

from sam_spot_bot_create_job.job_dao import JobDao
from .my_ut_config import create_env


@pytest.fixture
def init_env():
    create_env()


# TODO
def test_populate_file_meta_data(init_env):
    pass


def test_create_index(init_env):
    dao = JobDao()
    dao.create_index()


def test_insert(init_env):
    dao = JobDao()
    dao.save_file_list("ut-test-id", "ut-bucket", ["utkey1", "ut-key2"], 5)


def test_search_for_bot(init_env):
    dao = JobDao()
    # TODO Generate the ID for test.
    dao.search_file_list_for_bot("10d42b76-46fa-4ee2-87c8-79465216ff6f", "1", "NOT_STARTED")


def test_update_status_by_id(init_env):
    dao = JobDao()
    dao.update_status_by_id("58cb6e0e-153c-431d-abd3-0c30521dcf61")
