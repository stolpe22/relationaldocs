from abc import ABC, abstractmethod

from core.models.table import Table


class DatabaseReader(ABC):
    """Contrato de leitura de metadados — implementado por cada adapter de banco."""

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def fetch_schemas(self) -> list[str]: ...

    @abstractmethod
    def fetch_tables(self, schema: str) -> list[str]: ...

    @abstractmethod
    def fetch_metadata(self, schema: str, tables: list[str]) -> list[Table]: ...

    @abstractmethod
    def fetch_implicit_relations(
        self, schema: str, tables: list[str]
    ) -> dict[str, dict[str, list[str]]]:
        """Retorna {table_name: {column_name: [outras_tabelas_relacionadas]}}
        detectando vínculos pelo nome da coluna (COD%, NUM%) sem FK formal."""
        ...
