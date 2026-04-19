from fastapi import APIRouter, Depends, HTTPException

from adapters import get_reader
from adapters.ssh_tunnel import SSHTunnel
from api.dependencies import verify_api_key
from api.schemas.connection import (
    ConnectionRequest,
    ConnectionResponse,
    TunnelRequest,
    TunnelStatusResponse,
)
from api.state import AppState, ConnectionInfo, app_state
from core.exceptions import ConnectionError, TunnelError

router = APIRouter(prefix="/api/v1", tags=["connections"], dependencies=[Depends(verify_api_key)])


@router.post(
    "/connections/test",
    summary="Testa conexão com o banco",
    response_model=ConnectionResponse,
)
async def test_connection(body: ConnectionRequest) -> ConnectionResponse:
    reader_cls = get_reader(body.db_type)
    tunnel = app_state.tunnel
    active = tunnel is not None and tunnel.is_active
    actual_host = "127.0.0.1" if active else body.host
    actual_port = tunnel.local_bind_port if (active and tunnel) else body.port
    reader = reader_cls(
        host=actual_host,
        port=actual_port,
        service_name=body.service_name,
        connection_type=body.connection_type,
        user=body.user,
        password=body.password,
    )
    import logging
    logger = logging.getLogger("api.routers.connections")
    try:
        reader.connect()
        reader.disconnect()
        app_state.connection = ConnectionInfo(
            db_type=body.db_type,
            host=body.host,
            port=body.port,
            service_name=body.service_name,
            connection_type=body.connection_type,
            user=body.user,
            password=body.password,
        )
        return ConnectionResponse(success=True, message="Conexão bem-sucedida.")
    except ConnectionError as exc:
        logger.error(f"Erro ao testar conexão: {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/tunnels/open", summary="Abre túnel SSH", response_model=TunnelStatusResponse)
async def open_tunnel(body: TunnelRequest) -> TunnelStatusResponse:
    if app_state.tunnel and app_state.tunnel.is_active:
        raise HTTPException(status_code=400, detail="Túnel já está ativo.")
    tunnel = SSHTunnel(
        ssh_host=body.ssh_host,
        ssh_port=body.ssh_port,
        ssh_user=body.ssh_user,
        ssh_password=body.ssh_password,
        remote_host=body.remote_host,
        remote_port=body.remote_port,
    )
    try:
        tunnel.open()
        app_state.tunnel = tunnel
        return TunnelStatusResponse(active=True, local_port=tunnel.local_bind_port)
    except TunnelError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/tunnels/close", summary="Fecha túnel SSH", response_model=TunnelStatusResponse)
async def close_tunnel() -> TunnelStatusResponse:
    if app_state.tunnel:
        app_state.tunnel.close()
        app_state.tunnel = None
    return TunnelStatusResponse(active=False, local_port=None)


@router.get("/tunnels/status", summary="Estado do túnel SSH", response_model=TunnelStatusResponse)
async def tunnel_status() -> TunnelStatusResponse:
    if app_state.tunnel and app_state.tunnel.is_active:
        return TunnelStatusResponse(active=True, local_port=app_state.tunnel.local_bind_port)
    return TunnelStatusResponse(active=False, local_port=None)
