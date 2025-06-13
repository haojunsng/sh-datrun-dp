import json
import os
from pathlib import Path

import boto3


class S3Uploader:
    def __init__(self, bucket):
        self.env = os.getenv("ENV")
        self.s3 = boto3.client("s3")
        self.bucket = bucket
        self.local_export_dir = Path("local_exports")

    def upload(self, data, key):
        ENV = self.env

        if ENV == "prod":
            self.s3.put_object(
                Bucket=self.bucket, Key=key, Body=json.dumps(data)
            )
        else:
            self.local_export_dir.mkdir(exist_ok=True)
            local_path = self.local_export_dir / key
            local_path.parent.mkdir(parents=True, exist_ok=True)

            with open(local_path, "w") as f:
                json.dump(data, f, indent=2)
