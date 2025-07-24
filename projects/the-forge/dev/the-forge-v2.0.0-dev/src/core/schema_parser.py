from abc import ABC, abstractmethod
from typing import List
from .schema_field import SchemaField

class SchemaParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> List[SchemaField]:
        """Parse the schema file and return a list of SchemaField objects."""
        pass 