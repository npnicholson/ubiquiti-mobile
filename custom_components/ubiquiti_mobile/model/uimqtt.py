"""Module contains the uimqtt requests and responses."""

from pydantic import BaseModel

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
