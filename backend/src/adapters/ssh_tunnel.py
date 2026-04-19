import select
import socket
import threading

import paramiko

from core.exceptions import TunnelError
from core.interfaces.tunnel_manager import TunnelManager



class SSHTunnel(TunnelManager):
    def __init__(
        self,
        ssh_host: str,
        ssh_port: int,
        ssh_user: str,
        ssh_password: str,
        remote_host: str,
        remote_port: int,
    ) -> None:
        self._ssh_host = ssh_host
        self._ssh_port = ssh_port
        self._ssh_user = ssh_user
        self._ssh_password = ssh_password
        self._remote_host = remote_host
        self._remote_port = remote_port

        self._client: paramiko.SSHClient | None = None
        self._server_socket: socket.socket | None = None
        self._local_port: int = 0
        self._active: bool = False

    def open(self) -> None:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self._ssh_host,
                port=self._ssh_port,
                username=self._ssh_user,
                password=self._ssh_password,
                timeout=10,
            )
            client.get_transport().set_keepalive(30)

            # Local forwarding (único modo)
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", 0))
            srv.listen(5)
            local_port: int = srv.getsockname()[1]

            self._client = client
            self._server_socket = srv
            self._local_port = local_port
            self._active = True

            t = threading.Thread(target=self._accept_loop, daemon=True)
            t.start()

        except paramiko.AuthenticationException as exc:
            raise TunnelError(f"Autenticação SSH falhou: {exc}") from exc
        except paramiko.SSHException as exc:
            raise TunnelError(f"Erro SSH: {exc}") from exc
        except OSError as exc:
            raise TunnelError(f"Erro de rede: {exc}") from exc

    def close(self) -> None:
        self._active = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
            self._server_socket = None
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
        self._local_port = 0

    @property
    def local_bind_port(self) -> int:
        return self._local_port

    @property
    def is_active(self) -> bool:
        if not self._active:
            return False
        transport = self._client.get_transport() if self._client else None
        return transport is not None and transport.is_active()

    # ------------------------------------------------------------------

    def _accept_loop(self) -> None:
        srv = self._server_socket
        if srv is None:
            return
        srv.settimeout(1.0)
        while self._active:
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(
                target=self._forward,
                args=(conn, addr),
                daemon=True,
            ).start()

    def _forward(self, local_conn: socket.socket, addr: tuple[str, int]) -> None:
        transport = self._client.get_transport() if self._client else None
        if transport is None:
            local_conn.close()
            return
        try:
            channel = transport.open_channel(
                "direct-tcpip",
                (self._remote_host, self._remote_port),
                addr,
            )
        except Exception:
            local_conn.close()
            return

        try:
            while True:
                r, _, _ = select.select([local_conn, channel], [], [], 1.0)
                if local_conn in r:
                    data = local_conn.recv(4096)
                    if not data:
                        break
                    channel.sendall(data)
                if channel in r:
                    data = channel.recv(4096)
                    if not data:
                        break
                    local_conn.sendall(data)
        finally:
            local_conn.close()
            channel.close()
