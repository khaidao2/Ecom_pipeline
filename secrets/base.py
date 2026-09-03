from abc import ABC, abstractmethod
from typing import Dict


class SecretManager(ABC):
    
    @abstractmethod
    def get_all(self, path: str) -> Dict[str, str]:
        pass

    @abstractmethod
    def get(self, key: str, default: str = None) -> str:
        pass

    @abstractmethod
    def get_many(self, keys: list) -> Dict[str, str]:
        pass

    @abstractmethod
    def set(self, key: str, value: str):
        pass

    @abstractmethod
    def export_to_env(self, path: str, key_map: dict = None,
                      prefix: str = "VAULT") -> int:
        pass