import datetime

from firestore_client import FirestoreExporter
from s3_client import S3Uploader


def lambda_handler(event, context):

    try:
        # Extract collection_name from EventBridge detail
        collection_name = event.get("detail", {}).get("collection_name")
        s3_bucket = event.get("detail", {}).get("s3_bucket")

        if not collection_name:
            raise ValueError("collection_name not specified in event")

        # Validate collection
        ALLOWED_COLLECTIONS = {"users", "posts"}
        if collection_name not in ALLOWED_COLLECTIONS:
            raise ValueError(f"Invalid collection: {collection_name}")

        event_date = datetime.strptime(
            event["time"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%Y%m%d")

        exporter = FirestoreExporter()
        data = exporter.export_collection(
            collection_name=collection_name, date_of_execution=event_date
        )

        S3_KEY = (
            f"source=datrun/type={collection_name}/date={event_date}/data.json"
        )
        S3Uploader(bucket=s3_bucket).upload(data, S3_KEY)
    except Exception:
        raise
