import os
from typing import Dict
from .base import SecretManager

try:
    import hvac
except ImportError:
    hvac = None


class VaultSecret(SecretManager):
    """Read secrets from HashiCorp Vault (production)"""

    def __init__(self, url: str = None, token: str = None):
        self.url = url or os.getenv("VAULT_ADDR", "http://localhost:8200")
        self.token = token or os.getenv("VAULT_TOKEN")
        self.client = hvac.Client(url=self.url, token=self.token)

    def get(self, key: str, path: str = "secret/data/app", default: str = None) -> str:
        try:
            resp = self.client.secrets.kv.v2.read_secret_version(path=path)
            return resp["data"]["data"].get(key, default)
        except Exception:
            return default

    def get_many(self, keys: list, path: str = "secret/data/app") -> Dict[str, str]:
        try:
            resp = self.client.secrets.kv.v2.read_secret_version(path=path)
            return {key: resp["data"]["data"].get(key) for key in keys}
        except Exception:
            return {key: None for key in keys}

    def set(self, key: str, value: str, path: str = "secret/data/app"):
        try:
            current = self.get_many([], path)
            current[key] = value
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path, secret=current
            )
        except Exception as e:
            raise Exception(f"Failed to set secret: {e}")

    def read_secret(self, path: str) -> Dict[str, str]:
        """Read all key/value pairs of a secret path from Vault."""
        resp = self.client.secrets.kv.v2.read_secret_version(path=path)
        return resp["data"]["data"]

    def export_to_env(self, path: str, key_map: dict = None,
                      prefix: str = "VAULT") -> int:
        """Read a secret path on Vault and export each key to os.environ.

        key_map: maps {vault_key: env_var_name}.
                 If None, uses the vault key itself as the env var name.
        Returns number of keys exported.
        """
        data = self.read_secret(path)
        for k, v in data.items():
            env_name = key_map.get(k, k) if key_map else k
            os.environ[env_name] = str(v)
        return len(data)
