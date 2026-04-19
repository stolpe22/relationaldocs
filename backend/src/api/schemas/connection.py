from pydantic import BaseModel, ConfigDict, Field


class ConnectionRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    db_type: str = Field(default="oracle", pattern="^oracle$")
    host: str
    port: int = Field(ge=1, le=65535)
    service_name: str
    connection_type: str = Field(default="service_name", pattern="^(service_name|sid)$")
    user: str
    password: str
    schema_name: str | None = None


class ConnectionResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    success: bool
    message: str


class TunnelRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    ssh_host: str
    ssh_port: int = Field(default=22, ge=1, le=65535)
    ssh_user: str
    ssh_password: str
    remote_host: str
    remote_port: int = Field(ge=1, le=65535)


class TunnelStatusResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    active: bool
    local_port: int | None
