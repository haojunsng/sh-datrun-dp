import json
import os
from typing import Dict, List

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

    def export_collection(self, collection_name: str) -> List[Dict]:
        collection_ref = self.db.collection(collection_name)
        docs = collection_ref.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
