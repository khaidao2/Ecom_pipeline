import os
from typing import Dict
from .base import SecretManager


class EnvSecret(SecretManager):
    """Read secrets from environment variables (dev/staging)"""

    def __init__(self):
        pass

    def get_all(self, path: str = None) -> Dict[str, str]:
        """Return the whole environment. `path` kept for interface parity."""
        return dict(os.environ)

    def get(self, key: str, path: str = "secret/data/app", default: str = None) -> str:
        return os.getenv(key, default)

    def get_many(self, keys: list, path: str = "secret/data/app") -> Dict[str, str]:
        return {key: os.getenv(key) for key in keys}

    def set(self, key: str, value: str, path: str = "secret/data/app"):
        os.environ[key] = value

    def export_to_env(self, path: str, key_map: dict = None,
                      prefix: str = "VAULT") -> int:
        """Identity export for env source: values are already in os.environ.

        Only maps env var names when key_map is provided.
        """
        exported = 0
        for k, v in dict(os.environ).items():
            if key_map and k in key_map:
                os.environ[key_map[k]] = v
                exported += 1
        return exported
