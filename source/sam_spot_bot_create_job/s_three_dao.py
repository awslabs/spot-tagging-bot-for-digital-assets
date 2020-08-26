import boto3


class SimpleStorageServiceDao:

    def __init__(self, s3_bucket, s3_path, file_types: tuple):

        self.s3_bucket = s3_bucket
        self.s3_path = s3_path
        self.file_types = file_types
        self.s3 = boto3.client("s3")

    def get_file_list(self) -> list:
        """
            list file with filters.
        """
        print(
            ">>> going to list ALL files and it will take time - bkt:{}, path:{}".format(self.s3_bucket, self.s3_path))

        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.s3_bucket, Prefix=self.s3_path)

        all_key = []
        for page in pages:
            for obj in page['Contents']:
                all_key.append(obj['Key'])

        print("Found number of the files- {}, going to filter out for only {}".format(len(all_key), self.file_types))

        ft = tuple(self.file_types)
        print("filter files for {}".format(ft))
        filter_files = [x for x in all_key if str(x).endswith(ft)]

        print('<<< found {} files from s3://{}/{}'.format(len(filter_files), self.s3_bucket, self.s3_path))

        return filter_files
