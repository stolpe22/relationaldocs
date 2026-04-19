from dataclasses import dataclass, field
from typing import Any

from adapters.ssh_tunnel import SSHTunnel


@dataclass
class ConnectionInfo:
    db_type: str
    host: str
    port: int
    service_name: str
    connection_type: str
    user: str
    password: str


@dataclass
class AppState:
    tunnel: SSHTunnel | None = None
    connection: ConnectionInfo | None = None
    jobs: dict[str, dict[str, Any]] = field(default_factory=dict)


app_state = AppState()
