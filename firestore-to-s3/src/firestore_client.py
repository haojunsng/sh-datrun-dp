import json
import os
from datetime import datetime, timedelta
from typing import Dict, List

import pytz
from firebase_admin import credentials, firestore, initialize_app
from src.settings import AWS_REGION
from src.utils import _load_from_ssm


class FirestoreExporter:
    def __init__(self):
        self.env = os.getenv("ENV")
        self.db = self._initialize_firestore()

    def _initialize_firestore(self):
        ENV = self.env

        if ENV == "prod":
            param_name = os.environ["FIRESTORE_SSM_PARAM_NAME"]
            service_account_info = _load_from_ssm(param_name, AWS_REGION)
        else:
            json_path = os.environ.get("FIRESTORE_CREDENTIAL_PATH")
            service_account_info = self._load_from_file(json_path)

        cred = credentials.Certificate(service_account_info)

        try:
            return firestore.client()
        except Exception:
            initialize_app(cred)
            return firestore.client()

    def _load_from_file(self, path: str) -> Dict:
        with open(path, "r") as f:
            return json.load(f)

    def export_collection(
        self, collection_name: str, date_of_execution: str, days_back: int = 1
    ) -> List[Dict]:

        try:
            execution_date = datetime.strptime(
                date_of_execution, "%Y%m%d"
            ).replace(
                tzinfo=pytz.UTC, hour=0, minute=0, second=0, microsecond=0
            )
        except ValueError as e:
            raise ValueError(
                f"Invalid date format. Expected YYYYMMDD, "
                f"received: {date_of_execution}"
            ) from e

        # Calculate the delta
        left_limit = execution_date - timedelta(days=days_back)
        right_limit = execution_date

        # Convert to firestore timestamps
        start_timestamp = int(left_limit.timestamp() * 1000)
        end_timestamp = int(right_limit.timestamp() * 1000)

        collection_ref = self.db.collection(collection_name)
        query = collection_ref.where(
            "metadata.createdAt", ">=", start_timestamp
        ).where("metadata.createdAt", "<", end_timestamp)

        return [
            {
                "id": doc.id,
                **doc.to_dict(),
                "_export_window": {
                    "start_ts": start_timestamp,
                    "end_ts": end_timestamp,
                    "start_date": start_timestamp.strftime("%Y%m%d"),
                    "end_date": end_timestamp.strftime("%Y%m%d"),
                },
            }
            for doc in query.stream()
        ]
