import datetime
from .elasticsearch_helper import EsConnector
from .iam_helper import IamHelper
import time


class BotDao:
    """
    The key to BYOB (Bring your own bot) is to put bot configuration into the ES and allow the update from API.
    """

    INDEX_NAME = "bot_meta"

    def __init__(self):
        connector = EsConnector()
        self.es = connector.connect_es()
        helper = IamHelper()
        self.region = helper.get_region()

        self.create_index()
        # TODO Will be invoked many times. Python has no "static init" so it could be hard.
        self.create_default_bots()

    def create_index(self):
        """Creates an index in Elasticsearch if one isn't already there."""
        if not self.es.indices.exists(index=self.INDEX_NAME):
            self.es.indices.create(
                index=self.INDEX_NAME,
                body={
                    "mappings": {
                        "properties": {
                            "name": {"type": "keyword", "index": "true"},
                            "file_types": {"type": "keyword", "index": "true"},
                            "bot_image": {"type": "keyword", "index": "true"},
                            "bot_image_cmd": {"type": "keyword", "index": "true"},
                            "endpoint_ecr_image_path": {"type": "keyword", "index": "true"},
                            "instance_type": {"type": "keyword", "index": "true"},
                            "model_s3_path": {"type": "keyword", "index": "true"},
                            "create_date": {"type": "keyword", "index": "true"},
                            "update_date": {"type": "keyword", "index": "true"},
                        }
                    }
                },
                # ignore=400,
            )
            time.sleep(1)
            print("Bot meta index created - " + str(self.es.indices.exists(index=self.INDEX_NAME)))
        else:
            print("Index exists and don't create new.")

    def create_one_bot(self, name, file_types, bot_image, bot_image_cmd, endpoint_ecr_image_path, instance_type,
                       model_s3_path, create_date, update_date, endpoint_name):

        _doc = {
            "name": name,
            "file_types": file_types,
            "bot_image": bot_image,
            "bot_image_cmd": bot_image_cmd,
            "endpoint_name": endpoint_name,
            "endpoint_ecr_image_path": endpoint_ecr_image_path,
            "instance_type": instance_type,
            "model_s3_path": model_s3_path,
            "create_date": create_date,
            "update_date": update_date
        }
        print("Going to insert {}".format(str(_doc)))
        resp = self.es.index(
            index=self.INDEX_NAME,
            body=_doc
        )

        return resp

    def update_bot_by_name(self, name, file_types, bot_image, bot_image_cmd, endpoint_ecr_image_path, instance_type,
                           model_s3_path, create_date, update_date, endpoint_name) -> int:
        """
        :return The number of updated record.
        """
        q = {
            "script": {
                "inline": "ctx._source.name='" + name + "';" +
                          "ctx._source.file_types='" + file_types + "';" +
                          "ctx._source.bot_image='" + bot_image + "';" +
                          "ctx._source.bot_image_cmd='" + bot_image_cmd + "';" +
                          "ctx._source.endpoint_name='" + endpoint_name + "';" +
                          "ctx._source.endpoint_ecr_image_path='" + endpoint_ecr_image_path + "';" +
                          "ctx._source.instance_type='" + instance_type + "';" +
                          "ctx._source.model_s3_path='" + model_s3_path + "';" +
                          "ctx._source.create_date='" + create_date + "';" +
                          "ctx._source.update_date='" + update_date + "';",
            },
            "query": {
                "bool": {
                    "must": [
                        {"match": {"name": name}}
                    ]
                }
            }
        }
        print("Going to insert {}".format(str(q)))
        resp = self.es.update_by_query(
            index=self.INDEX_NAME,
            body=q
        )

        return resp["updated"]

    def delete_bot_by_name(self, name):
        q = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"name": name}}
                    ]
                }
            }
        }
        return self.es.delete_by_query(
            index=self.INDEX_NAME,
            body=q
        )

    def get_bot_def(self, bot_name: str):
        """
        Get the bot config.
        :return: {
                    "name": "CAR_ACCIDENT_INSPECTOR",
                    "file_types": [".jpg", ".png"],
                    'bot_image': self.bot_car_accident_inspector_bot_image,
                    'bot_image_cmd': "",
                    'endpoint_name': "autogluon-sagemaker-inference",
                    'endpoint_ecr_image_path': self.bot_car_accident_inspector_endpoint_image,
                    'instance_type': "ml.m5.large",
                    'model_s3_path': ""
                }
        """
        query = {
            "size": 1,
            "query": {
                "bool": {
                    "must": [
                        {"match": {"name": bot_name}}
                    ]
                }
            }
        }
        print(">>> bot: going to query: {}".format(query))

        resp = self.es.search(
            index=self.INDEX_NAME,
            body=query
        )

        hit = resp['hits']['hits']
        print("DOC COUNT:", len(hit))
        if len(hit) < 1:
            return None
        return hit[0]["_source"]

    def delete_index(self):
        print("<<< Going to DELETE index with name {}!!!".format(self.INDEX_NAME))
        try:
            self.es.indices.delete(index=self.INDEX_NAME)
            print(">>> deleted index.")
        except Exception as e:
            print("Cannot delete index. " + str(e))

    def create_default_bots(self):
        if self.get_bot_def("CAR_ACCIDENT_INSPECTOR") is None:
            bot_def = {
                "name": "CAR_ACCIDENT_INSPECTOR",
                "file_types": [".jpg", ".png", ".jpeg"],
                'bot_image_cmd': "",
                'endpoint_name': "autogluon-sagemaker-inference",
                'instance_type': "ml.m5.large",
                'model_s3_path': "",
                'create_date': datetime.datetime.utcnow(),
                'update_date': datetime.datetime.utcnow()
            }
            # deal add ecr global region/china region difference
            if self.region in ['cn-north-1', 'cn-northwest-1']:
                bot_def['bot_image'] = "753680513547.dkr.ecr." + self.region + ".amazonaws.com.cn/autogluon-sagemaker-inference-bot:latest"
                bot_def['endpoint_ecr_image_path'] = "753680513547.dkr.ecr." + self.region + ".amazonaws.com.cn/autogluon-sagemaker-inference:latest"
            else:
                bot_def['bot_image'] = "366590864501.dkr.ecr." + self.region + ".amazonaws.com/autogluon-sagemaker-inference-bot:latest"
                bot_def['endpoint_ecr_image_path'] = "366590864501.dkr.ecr." + self.region + ".amazonaws.com/autogluon-sagemaker-inference"

            self.create_one_bot(**bot_def)
            # To deal with the final consistency.
            # This only affect init the first time because it doesn't invoke later on.
            time.sleep(1)

            print("created the default bot: CAR_ACCIDENT_INSPECTOR")

        if self.get_bot_def("CHINESE_ID_OCR") is None:
            bot_def = {
                "name": "CHINESE_ID_OCR",
                "file_types": [".jpg", ".jpeg", ".png"],
                'bot_image_cmd': "",
                'endpoint_name': "ocr-ctpn,OCR-CRNN",
                'instance_type': "ml.m5.large",
                'model_s3_path': "s3://aws-solutions-" + self.region + "/spot-bot-models/ctpn.tar.gz,s3://aws-solutions-" + self.region + "/spot-bot-models/crnn-general.tar.gz",
                'create_date': datetime.datetime.utcnow(),
                'update_date': datetime.datetime.utcnow()
            }
            # deal add ecr global region/china region difference
            if self.region in ['cn-north-1', 'cn-northwest-1']:
                bot_def['bot_image'] = "753680513547.dkr.ecr." + self.region + ".amazonaws.com.cn/id_ocr_bot:latest"
                bot_def['endpoint_ecr_image_path'] = "753680513547.dkr.ecr." + self.region + ".amazonaws.com.cn/ocr-ctpn-endpoint,753680513547.dkr.ecr." + self.region + ".amazonaws.com.cn/ocr-crnn-endpoint"
            else:
                bot_def['bot_image'] = "366590864501.dkr.ecr." + self.region + ".amazonaws.com/id_ocr_bot:latest"
                bot_def['endpoint_ecr_image_path'] = "366590864501.dkr.ecr." + self.region + ".amazonaws.com/ocr-ctpn-endpoint,366590864501.dkr.ecr." + self.region + ".amazonaws.com/ocr-crnn-endpoint"
            self.create_one_bot(**bot_def)
            time.sleep(1)
            print("created the default bot: CHINESE_ID_OCR")

        if self.get_bot_def("SENTIMENT_ANALYSIS") is None:
            bot_def = {"name": "SENTIMENT_ANALYSIS", "file_types": [".txt"], 'bot_image_cmd': "",
                       'endpoint_name': "bert-sentiment", 'instance_type': "ml.m5.large",
                       'create_date': datetime.datetime.utcnow(), 'update_date': datetime.datetime.utcnow(),
                       'model_s3_path': "s3://aws-solutions-" + self.region + "/spot-bot-models/sentiment-model.tar.gz"}
            #set s3 path to be regional
            # deal add ecr global region/china region difference
            if self.region in ['cn-north-1', 'cn-northwest-1']:
                bot_def['bot_image'] = "753680513547.dkr.ecr." + self.region + ".amazonaws.com.cn/sentiment-analysis-bot:latest"
                bot_def['endpoint_ecr_image_path'] = "753680513547.dkr.ecr." + self.region + ".amazonaws.com.cn/sentiment-analyisis-endpoint:latest"
            else:
                bot_def['bot_image'] = "366590864501.dkr.ecr." + self.region + ".amazonaws.com/sentiment-analysis-bot:latest"
                bot_def['endpoint_ecr_image_path'] = "366590864501.dkr.ecr." + self.region + ".amazonaws.com/sentiment-analyisis-endpoint:latest"
            self.create_one_bot(**bot_def)
            time.sleep(1)
            print("created the default bot: SENTIMENT_ANALYSIS")


