from abc import ABC, abstractmethod


class TunnelManager(ABC):
    """Contrato de gerenciamento de túnel SSH."""

    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @property
    @abstractmethod
    def local_bind_port(self) -> int: ...

    @property
    @abstractmethod
    def is_active(self) -> bool: ...
