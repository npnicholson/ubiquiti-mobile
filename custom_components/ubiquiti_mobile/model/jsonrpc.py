"""Module contains the JSON RPC Request and Response classes."""

from typing import TypeVar

from pydantic import BaseModel

Params = TypeVar("Params")
Error = TypeVar("Error")
Result = TypeVar("Result")


class JSONRPCBase(BaseModel):
    """Class that reflects the elements common to both requests and responses."""

    jsonrpc: str = "2.0"
    id: int | None = None


class Request[Params](JSONRPCBase):
    """Class that reflects a devices response."""

    method: str = ""
    params: Params | None = None


class Response[Result, Error](JSONRPCBase):
    """Class that reflects a devices response."""

    result: Result | None = None
    error: Error | None = None


class GenericError(BaseModel):
    """Class that reflects a generic jsonrpc error."""

    code: int
    message: str
