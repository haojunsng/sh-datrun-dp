import datetime

from src.firestore_client import FirestoreExporter
from src.s3_client import S3Uploader


def lambda_handler(event, context):

    event_time = datetime.strptime(event["time"], "%Y-%m-%dT%H:%M:%SZ")
    partition_date = event_time.strftime("%Y%m%d")

    exporter = FirestoreExporter()

    uploader = S3Uploader(bucket="my-bucket")
    S3_KEY = f"source=datrun/type=post/" f"date={partition_date}/" f"data.json"

    data = exporter.get_collection("test")
    uploader.upload(data, S3_KEY)
