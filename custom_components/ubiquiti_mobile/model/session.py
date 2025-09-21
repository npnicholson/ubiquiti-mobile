"""API Structure for creating a new session."""

from pydantic import BaseModel, Field

from custom_components.ubiquiti_mobile.model.jsonrpc import Request, Response

# ---------------------------
# Pydantic Models
# ---------------------------

SESSION_PATH = "/ubus/call/session"
SESSION_METHOD = "post"


class SessionParams(BaseModel):
    """Parameters within the Session Request."""

    username: str
    password: str
    timeout: int = Field(..., description="Session timeout in seconds")


class ACLs(BaseModel):
    """Access control lists within the Session Result."""

    access_group: dict[str, list[str]] | None = Field(alias="access-group")
    ubus: dict[str, list[str]] | None
    uimqtt: dict[str, list[str]] | None


class SessionData(BaseModel):
    """Nested data within the Session Result - Username."""

    username: str


class SessionRequest(Request[SessionParams]):
    """Request format for jsonrpc."""

    method: str = "login"
    params: SessionParams | None = None


class SessionResult(Response):
    """Result format for jsonrpc."""

    ubus_rpc_session: str
    timeout: int
    expires: int
    acls: ACLs
    data: SessionData
