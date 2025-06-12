import json
import os
from typing import Dict, List

import boto3
from firebase_admin import credentials, firestore, initialize_app


class FirestoreExporter:
    def __init__(self):
        self.db = self._initialize_firestore()

    def _initialize_firestore(self):
        ENV = os.getenv("ENV")

        if ENV == "prod":
            param_name = os.environ["FIRESTORE_SSM_PARAM_NAME"]
            region = os.environ.get("AWS_REGION", "ap-southeast-1")
            service_account_info = self._load_from_ssm(param_name, region)
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

    def _load_from_ssm(self, param_name: str, region: str) -> Dict:
        ssm = boto3.client("ssm", region_name=region)
        response = ssm.get_parameter(Name=param_name, WithDecryption=True)
        return json.loads(response["Parameter"]["Value"])

    def export_collection(self, collection_name: str) -> List[Dict]:
        collection_ref = self.db.collection(collection_name)
        docs = collection_ref.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
