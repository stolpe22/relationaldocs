from abc import ABC, abstractmethod

from core.models.table import Table


class MarkdownRenderer(ABC):
    """Contrato de renderização de tabela para markdown."""

    @abstractmethod
    def render(self, table: Table) -> str: ...
