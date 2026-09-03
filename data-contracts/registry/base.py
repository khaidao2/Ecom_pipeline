from typing import Dict
from abc import ABC, abstractmethod

class Registry(ABC):

  @abstractmethod
  def get_version(self, schema_id:str) -> int:
    pass

  @abstractmethod
  def get_schema(self, schema_id:str) -> dict:
    pass

  @abstractmethod
  def register(self,schema_path) -> Dict:
    pass

  @abstractmethod
  def validate(self, schema_id: str, data: Dict) -> bool:
    pass