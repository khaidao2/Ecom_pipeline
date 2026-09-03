import json
import logging
import os
import requests
from typing import Dict
from .base import Registry

logger = logging.getLogger(__name__)


class ApicurioRegistry(Registry):

    def __init__(self, base_url: str = None):
        if base_url is None:
            base_url = os.getenv("APICURIO_REGISTRY_URL", "http://localhost:8080")
        self.base_url = base_url.rstrip("/")
        self.api = f"{self.base_url}/apis/registry/v2"

    def register(self, schema_path: str, group_id: str = "default") -> Dict:
        with open(schema_path) as f:
            schema = json.load(f)

        artifact_id = schema.get("name", schema_path.split("/")[-1].replace(".avsc", ""))

        resp = requests.put(
            f"{self.api}/groups/{group_id}/artifacts/{artifact_id}",
            headers={
                "Content-Type": "application/json",
                "X-Registry-ArtifactType": "AVRO"
            },
            data=json.dumps(schema)
        )
        resp.raise_for_status()

        global_id = resp.headers.get("X-Registry-Global-Id")
        version = resp.headers.get("X-Registry-Version")

        logger.info(f"Registered {group_id}/{artifact_id} globalId={global_id} v{version}")

        return {
            "globalId": int(global_id),
            "version": int(version),
            "artifactId": artifact_id,
            "groupId": group_id
        }

    def get_id(self, artifact_id: str, group_id: str = "default") -> int:
        resp = requests.get(f"{self.api}/groups/{group_id}/artifacts/{artifact_id}/meta")
        resp.raise_for_status()
        return resp.json()["globalId"]

    def get_schema(self, schema_id: str) -> dict:
        resp = requests.get(f"{self.api}/artifacts/{schema_id}")
        resp.raise_for_status()
        return resp.json()

    def get_version(self, schema_id: str) -> int:
        resp = requests.get(f"{self.api}/artifacts/{schema_id}/versions")
        resp.raise_for_status()
        versions = resp.json()
        return max(v["version"] for v in versions)

    def validate(self, schema_id: str, data: Dict) -> bool:
        try:
            from fastavro import parse_schema, validate as avro_validate
            schema = self.get_schema(schema_id)
            parse_schema(schema)
            avro_validate(data, schema=schema)
            return True
        except Exception as e:
            logger.error(f"Validation failed for {schema_id}: {e}")
            return False
