import json
from typing import Dict

import boto3
from src.settings import AWS_REGION


def _load_from_ssm(self, param_name: str, region: str) -> Dict:
    ssm = boto3.client("ssm", region_name=AWS_REGION)
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return json.loads(response["Parameter"]["Value"])
