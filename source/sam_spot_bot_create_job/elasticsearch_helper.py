import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from .config import PlannerConfig


class EsConnector:
    """
    ES request sign.
    https://github.com/aws-samples/amazon-textract-comprehend-OCRimage-search-and-analyze/blob/master/lambda/comprehend.py
    """

    def __init__(self):
        print('setting up boto3')

        self._config = PlannerConfig()
        # root = os.environ["LAMBDA_TASK_ROOT"]
        # sys.path.insert(0, root)
        print(boto3.__version__)
        print('core path setup')

        self.host = self._config.esDomain
        self.port = self._config.esPort
        self.region = boto3.session.Session().region_name

        self.service = 'es'
        self.credentials = boto3.Session().get_credentials()

    def connect_es(self) -> Elasticsearch:

        print('>>> Connecting to the ES Endpoint {}://{}:{}'.format(self._config.esProtocol, self.host, self.port))
        try:
            if self._config.esProtocol == "http":
                self.es = Elasticsearch(
                    hosts=[{'host': self.host, 'port': self.port}],
                    # http_auth=awsauth,
                    connection_class=RequestsHttpConnection)
            else:
                self.es = Elasticsearch(
                    hosts=[{'host': self.host, 'port': self.port}],
                    use_ssl=True
                )

        except Exception as E:
            print("Unable to connect to {0}")
            print(E)
            exit(3)

        return self.es

    def get_es_url(self):
        return '{}:{}'.format(self.host, self.port)
