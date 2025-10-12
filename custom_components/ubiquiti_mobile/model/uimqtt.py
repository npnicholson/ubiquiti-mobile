"""Module contains the uimqtt requests and responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from .jsonrpc import Request

UIMQTT_PATH = "/ubus/call/uimqtt"
UIMQTT_METHOD = "post"


####################################################################################################
# Get Device Info
####################################################################################################
class GetDeviceInfoRequest(Request):
    """Class that reflects a GetDeviceInfo uimqtt request."""

    method: str = "GetDeviceInfo"
    params: None = None


class GetDeviceInfoResponse(BaseModel):
    """Class that reflects a response from a GetDeviceInfo Request."""

    board_revision: str
    mac: str
    model_name: str
    lte_model_name: str
    cloud_url: str
    device_ac: str
    imei: str
    bridge_mode: bool
    wan_ip: str
    lan_ip: str


####################################################################################################
# Get GPS Info
####################################################################################################
class GetGPSInfoRequest(Request):
    """Class that reflects a GetGPSInfo uimqtt request."""

    method: str = "InfoGpsDump"
    params: None = None


class GetGPSInfoResponse(BaseModel):
    """Class that reflects a response from a GetGPSInfo Request."""

    latitude: float
    longitude: float
    quality: int
    timestamp: int
    hdop: float


####################################################################################################
# Get Network Info
####################################################################################################


class GetHighInfoRequest(Request[dict[str, str]]):
    """Class that reflects a InfoHighDump uimqtt request."""

    method: str = "InfoHighDump"
    params: None = None


class HighClientInfo(BaseModel):
    """Represents information about a connected client."""

    ip: str
    mac: str
    id: int
    connection: str
    host_name: str
    rxPackets: int  # noqa: N815
    txPackets: int  # noqa: N815
    rxBytes: int  # noqa: N815
    txBytes: int  # noqa: N815
    rxAggrBytes: int  # noqa: N815
    txAggrBytes: int  # noqa: N815
    uptime: int | None = None
    tx_rate: int | None = None
    rx_rate: int | None = None
    link_speed: int | None = None
    ssid: str | None = None
    band: str | None = None
    channel: int | None = None
    bandwidth: int | None = None
    signal: int | None = None
    mode: str | None = None
    associated_at: int | None = None
    rxBitRate: int | None = None  # noqa: N815
    txBitRate: int | None = None  # noqa: N815
    score: int | None = None
    per: int | None = None


class GetHighInfoResponse(BaseModel):
    """Class that reflects a response from a InfoHighDump Request."""

    fw: str
    uptime: int
    iccid: str
    imsi: str
    apn: str
    lte_apn_username: str
    lte_apn_password: str
    lte_apn_auth_type: str
    lte_roaming_allowed: bool
    lte_mode: str
    lte_band: str
    lte_4g_band: str
    signal_level: int
    operator_name: str
    ip: str
    network_source: str
    geo_ip: str
    geo_isp: str
    upload_usage: int
    download_usage: int
    total_usage: int
    upload_speed: int
    download_speed: int
    client_numbers: int
    experience: int
    per: int
    wifi_clients: int
    sample_time: int
    cpu: int
    memory: int
    latency_avg_ms: int
    latency_max_ms: int
    latency_sample_count: int
    latency_packet_loss_count: int
    reset_usage_timestamp: int
    clients: int
    sample_count: int
    sample_interval_second: int
    lte_state: int
    rssi: int
    rsrq: int
    rsrp: int
    rx_channel: int
    tx_channel: int
    band: str
    wifi_wan_status_code: int
    download_usage_avg: int
    upload_usage_avg: int
    client_details: list[HighClientInfo] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _extract_clients(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Collect client objects (client0, client1, ...) into client_details."""
        if not isinstance(values, dict):
            return values

        client_entries: list[dict[str, Any]] = []
        client_keys: list[str] = []

        for key, val in values.items():
            if key.startswith("client") and key[6:].isdigit() and isinstance(val, dict):
                client_entries.append(val)
                client_keys.append(key)

        for key in client_keys:
            values.pop(key)

        if client_entries:
            values["client_details"] = client_entries

        return values
