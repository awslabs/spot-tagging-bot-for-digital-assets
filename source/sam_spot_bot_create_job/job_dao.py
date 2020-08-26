import datetime
import math
import uuid

from elasticsearch.helpers import streaming_bulk

from .elasticsearch_helper import EsConnector


class JobDao:
    """
    This class is to save and retrieve the S3 file info and how the Job should be executed.
    ES request sign.
    https://github.com/aws-samples/amazon-textract-comprehend-OCRimage-search-and-analyze/blob/master/lambda/comprehend.py
    """

    INDEX_NAME = "spot_bot"

    def __init__(self):
        connector = EsConnector()
        self.es = connector.connect_es()

    def create_index(self):
        """Creates an index in Elasticsearch if one isn't already there."""
        self.es.indices.create(
            index=self.INDEX_NAME,
            body={
                "mappings": {
                    "properties": {
                        "bucket": {"type": "keyword", "index": "true"},
                        "file_key": {"type": "keyword", "index": "true"},
                        "status": {"type": "keyword", "index": "true"},
                        "create_date": {"type": "date"},
                        "complete_date": {"type": "date"},
                        "batch_id": {"type": "keyword", "index": "true"}
                    }
                },
            },
            ignore=400,
        )

    def save_file_list(self, job_id, bucket, file_list: list, number_of_bots):
        """
        https://github.com/elastic/elasticsearch-py/blob/master/examples/bulk-ingest/bulk-ingest.py
        record processing status: NOT_STARTED, PROCESSING, ERROR, COMPLETED
        :param number_of_bots:
        """
        print("Creating an index...")
        self.create_index()

        print(">>> Indexing documents...")
        successes = 0

        # now = datetime.datetime.utcnow()
        for ok, action in streaming_bulk(
                client=self.es,
                index=self.INDEX_NAME,
                actions=self.__record_generator(job_id, bucket, file_list, number_of_bots),
        ):
            successes += ok
        print(">>> Number of records saved to ES: {}".format(successes))

    def search_file_list_for_bot(self, job_id: str, batch_id: str, status: str):
        """
        Fot bot to get their file to process.
        :param job_id: One customer request for bots to process on certain folder is one *job*, and thus have a job_id.
        :param batch_id: Files in one job will spited based on the number of bots. Bot id and batch id is the same.
        :param status: one of "NOT_STARTED, COMPLETED, PROCESSING"
        :return:
        """
        query = {  # TODO Would speed up by reduce the result fields
            "size": 10000,
            "query": {
                "bool": {
                    "must": [
                        {"match": {"job_id": job_id}},
                        {"match": {"batch_id": batch_id}},
                        {"match": {"status": status}}
                    ]
                }
            }
        }
        print(">>> going to query: {}".format(query))

        resp = self.es.search(
            index=self.INDEX_NAME,
            body=query,
            scroll='9s'
        )

        # keep track of pass scroll _id
        old_scroll_id = resp['_scroll_id']
        all_hits = resp['hits']['hits']
        # use a 'while' iterator to loop over document 'hits'
        while len(resp['hits']['hits']):

            # make a request using the Scroll API
            resp = self.es.scroll(
                scroll_id=old_scroll_id,
                scroll='2s'  # length of time to keep search context
            )

            # check if there's a new scroll ID
            if old_scroll_id != resp['_scroll_id']:
                print("NEW SCROLL ID:", resp['_scroll_id'])

            # keep track of pass scroll _id
            old_scroll_id = resp['_scroll_id']

            # print the response results
            print("\nresponse for index:", self.INDEX_NAME)
            print("_scroll_id:", resp['_scroll_id'])
            print('response["hits"]["total"]["value"]:{}'.format(resp["hits"]["total"]))

            # iterate over the document hits for each 'scroll'
            all_hits.extend(resp['hits']['hits'])
        print("DOC COUNT:", len(all_hits))

        return all_hits

    def delete_index(self):
        print("<<< Going to DELETE index!!!")
        try:
            self.es.delete_by_query(index=self.INDEX_NAME, body={"query": {"match_all": {}}})
        except Exception as e:
            print("Cannot delete index. " + str(e))

    def update_status_by_id(self, doc_id, status="COMPLETED"):

        resp = self.es.update(
            index=self.INDEX_NAME,
            id=doc_id,
            body={
                "doc":
                    {"status": status,
                     "complete_date": datetime.datetime.utcnow()
                     }
            },
            doc_type="_doc"
        )

        return resp

    @staticmethod
    def __record_generator(job_id, bucket, file_list: list, number_of_bots):
        now = datetime.datetime.utcnow()
        # iso_now = now.strftime('%Y-%m-%dT%H:%M:%S') + now.strftime('.%f')[:4] + 'Z'
        f_len = len(file_list)
        for i, k in enumerate(file_list):  # i start from 0.
            record = {
                "_id": str(uuid.uuid4()),
                "_type": "_doc",
                "job_id": job_id,
                "bucket": bucket,
                "file_key": k,
                "status": "NOT_STARTED",
                "created_date:": now,
                "output": "",
                "batch_id": math.ceil((i + 1) / (f_len / number_of_bots))  # every bot will get an ID starting from 1...
            }
            yield record
