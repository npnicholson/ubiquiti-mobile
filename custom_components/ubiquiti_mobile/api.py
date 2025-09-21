"""Sample API Client."""

from __future__ import annotations

import socket
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout
from pydantic import TypeAdapter

from custom_components.ubiquiti_mobile.model.jsonrpc import Response
from custom_components.ubiquiti_mobile.model.uimqtt import UIMQTT_METHOD, UIMQTT_PATH

from .const import LOGGER
from .model.session import (
    SESSION_METHOD,
    SESSION_PATH,
    SessionParams,
    SessionRequest,
    SessionResult,
)
from .model.uimqtt import (
    GetDeviceInfoRequest,
    GetDeviceInfoResponse,
    GetGPSInfoRequest,
    GetGPSInfoResponse,
    GetHighInfoRequest,
    GetHighInfoResponse,
)

if TYPE_CHECKING:
    from .data import SessionData


class UbiquitiMobileApiClientError(Exception):
    """Exception to indicate a general API error."""


class UbiquitiMobileApiClientCommunicationError(
    UbiquitiMobileApiClientError,
):
    """Exception to indicate a communication error."""


class UbiquitiMobileApiClientAuthenticationError(
    UbiquitiMobileApiClientError,
):
    """Exception to indicate an authentication error."""


async def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise UbiquitiMobileApiClientAuthenticationError(
            msg,
        )

    # Handle response errors including authentication
    data = await response.json()
    if "error" in data:
        if (
            data["error"]["message"] == "Access denied"
            or data["error"]["message"] == "Permission denied"
        ):
            msg = "Invalid credentials"
            raise UbiquitiMobileApiClientAuthenticationError(
                msg,
            )

        msg = data["error"]["message"]
        raise UbiquitiMobileApiClientError(
            msg,
        )

    response.raise_for_status()


class UbiquitiMobileApiClient:
    """API client for Ubiquiti Mobile Gateway."""

    def __init__(
        self, session_data: SessionData, session: aiohttp.ClientSession
    ) -> None:
        """Initialize the API client."""
        self._session_data: SessionData = session_data
        self._session = session

    async def get_device_info(self) -> Response[GetDeviceInfoResponse, Any]:
        """Call GetDeviceInfo using the router API."""
        response_dict = await self._api_wrapper(
            method=UIMQTT_METHOD,
            path=UIMQTT_PATH,
            data=GetDeviceInfoRequest().model_dump(),
        )

        return TypeAdapter(Response[GetDeviceInfoResponse, Any]).validate_python(
            response_dict
        )

    async def get_gps_info(self) -> Response[GetGPSInfoResponse, Any]:
        """Call GetGPSInfo using the router API."""
        response_dict = await self._api_wrapper(
            method=UIMQTT_METHOD,
            path=UIMQTT_PATH,
            data=GetGPSInfoRequest().model_dump(),
        )

        return TypeAdapter(Response[GetGPSInfoResponse, Any]).validate_python(
            response_dict
        )

    async def get_high_info(self) -> Response[GetHighInfoResponse, Any]:
        """Call InfoHighDump using the router API."""
        response_dict = await self._api_wrapper(
            method=UIMQTT_METHOD,
            path=UIMQTT_PATH,
            data=GetHighInfoRequest().model_dump(),
        )

        return TypeAdapter(Response[GetHighInfoResponse, Any]).validate_python(
            response_dict
        )

    async def async_start_session(self) -> Response[SessionResult, Any]:
        """Authenticate with the gateway and store token in session."""
        if (
            self._session_data.username is not None
            and self._session_data.password is not None
            and self._session_data.host is not None
        ):
            # Build the session request model
            req_model = SessionRequest(
                params=SessionParams(
                    username=self._session_data.username,
                    password=self._session_data.password,
                    timeout=2129920,
                )
            )

            try:
                # Send a request to get a new session token. Verify the response is a
                # 200 ok and that it has the correct data. Then save the token to self
                # and return.
                async with async_timeout.timeout(10):
                    response = await self._session.request(
                        ssl=False,
                        method=SESSION_METHOD,
                        url="https://" + self._session_data.host + SESSION_PATH,
                        headers={
                            "Content-type": "application/json; charset=UTF-8",
                        },
                        json=req_model.model_dump(),
                    )
                    await _verify_response_or_raise(response)

                    json_data = await response.json()

                    resp_model = Response[SessionResult, Any](**json_data)

                    if resp_model.result is None:
                        msg = "No result returned from gateway"
                        raise ValueError(msg)

                    self._session_data.token = resp_model.result.ubus_rpc_session

                    if not self._session_data.token:
                        msg = "No token returned from gateway"
                        raise ValueError(msg)

                    return resp_model

            except TimeoutError as exception:
                msg = f"Timeout error fetching information - {exception}"
                raise UbiquitiMobileApiClientCommunicationError(
                    msg,
                ) from exception
            except (aiohttp.ClientError, socket.gaierror) as exception:
                msg = f"Error fetching information - {exception}"
                raise UbiquitiMobileApiClientCommunicationError(
                    msg,
                ) from exception
        else:
            msg = "Username, password, or host not provided for authentication"
            raise UbiquitiMobileApiClientAuthenticationError(
                msg,
            )

    async def _api_wrapper(
        self,
        method: str,
        path: str,
        data: dict | None = None,
    ) -> Any:
        """Get information from the API. If not authenticated, attempt to do so."""
        # If we do not have a session token, then try to get one
        if self._session_data.token is None:
            await self.async_start_session()

        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    ssl=False,
                    method=method,
                    url=f"https://{self._session_data.host}{path}",
                    headers={
                        "Content-type": "application/json; charset=UTF-8",
                        "Authorization": "Bearer "
                        + (self._session_data.token or "none"),
                    },
                    json=data,
                )
                await _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise UbiquitiMobileApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise UbiquitiMobileApiClientCommunicationError(
                msg,
            ) from exception
        except UbiquitiMobileApiClientAuthenticationError as exception:
            LOGGER.warning(f"Resetting session due to auth error - {exception}")

            # This will throw an authentication error if it can't sign in. Because it is
            # not protected with a try/except, recursion won't occur in that case
            await self.async_start_session()
            return await self._api_wrapper(method, path, data)
