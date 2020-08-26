import os

import pytest
from sam_spot_bot_create_job.config import PlannerConfig
from .my_ut_config import create_env


@pytest.fixture
def init_env():
    create_env()


def test_es_config():
    os.environ["ES_URL"] = "vpc-spot-bot-asyx7xoeosm6xyysm4vcyjkge4.us-east-2.es.amazonaws.com"
    config = PlannerConfig()
    assert str(config.esProtocol) == 'https'
    assert config.esDomain == 'vpc-spot-bot-asyx7xoeosm6xyysm4vcyjkge4.us-east-2.es.amazonaws.com'
    assert config.esPort == '443'


def test_es_config_1():
    os.environ["ES_URL"] = "http://121.121.121.121:8088"
    config = PlannerConfig()
    assert str(config.esProtocol) == 'http'
    assert config.esDomain == '121.121.121.121'
    assert config.esPort == '8088'


def test_es_config_2():
    os.environ["ES_URL"] = "https://121.121.121.121"
    config = PlannerConfig()
    assert str(config.esProtocol) == 'https'
    assert config.esDomain == '121.121.121.121'
    assert config.esPort == '443'


def test_cpu_batch_min():
    os.environ["ES_URL"] = "https://121.121.121.121"
    config = PlannerConfig()
    assert config.batch_EC2_vCPU_MIN == 0
