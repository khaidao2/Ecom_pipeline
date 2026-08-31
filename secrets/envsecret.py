import os
from typing import Dict
from .base import SecretManager


class EnvSecret(SecretManager):
    """Read secrets from environment variables (dev/staging)"""

    def __init__(self):
        pass

    def get(self, key: str, default: str = None) -> str:
        return os.getenv(key, default)

    def get_many(self, keys: list) -> Dict[str, str]:
        return {key: os.getenv(key) for key in keys}

    def set(self, key: str, value: str):
        os.environ[key] = value
