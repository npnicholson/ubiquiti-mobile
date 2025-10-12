# Ubiquiti Mobile for Home Assistant

This custom integration authenticates against the local JSON-RPC interface of a Ubiquiti Mobile Gateway and exposes its status in Home Assistant. Once configured the integration polls the gateway every five seconds, surfaces network telemetry, and keeps GPS data in sync so you can build automations around connectivity and location.

## Features

### Gateway Sensors

- `Wan Ip Address` / `Lan Ip Address` report the WAN and LAN assignments advertised by the router.
- `Data Usage`, `Upload Usage`, and `Download Usage` expose cumulative traffic counters in bytes.
- `Clients` reflects the number of concurrently connected devices.
- `Uptime`, `CPU Usage`, `Memory Usage`, and `Experience` highlight system health.
- `RSSI` surfaces the current cellular signal strength in dBm.

### Client Tracking

- Every client in the `InfoHighDump` payload appears as a Home Assistant device with a `router`-source tracker entity.
- Each client gets dedicated sensors for `Connection Type`, `IP Address`, and live `Receive` / `Transmit` throughput (bytes per second), working for both wired and wireless clients.

### GPS Tracking

- A `Location` tracker publishes latitude and longitude whenever GPS data is available from the gateway.

## Requirements

- Local access to a Ubiquiti Mobile Gateway running firmware with the `/ubus/call` API enabled.
- Administrator credentials for the gateway (the stock username is usually `ui`).
- Home Assistant 2025.2.4 or newer, as defined in `hacs.json`.
- Your Home Assistant host must be able to reach `https://<gateway-ip>` on the local network. SSL verification is skipped, so the gateway's self-signed certificate is accepted automatically.

## Installation

### HACS (recommended)

- In HACS, open Integrations → ⋮ → `Custom repositories`, and add `https://github.com/npnicholson/ubiquiti-mobile` as an Integration repository.
- Install **Ubiquiti Mobile** from the HACS Integrations catalog.
- Restart Home Assistant to load the integration.

### Manual installation

- Copy `custom_components/ubiquiti_mobile` into your Home Assistant `config/custom_components` directory.
- Restart Home Assistant.

## Configuration

- Go to Settings → Devices & Services in Home Assistant and click `+ Add Integration`.
- Search for **Ubiquiti Mobile**.
- Enter the gateway host or IP address (for example `192.168.1.1`), along with the username and password for your local admin account. The username defaults to `ui` in the form.
- Submit the form to test the connection. The integration authenticates, stores the resulting session token, and creates a device for the gateway.
- After setup you will find a gateway device (named using the router's MAC address and model) containing the sensors above. Client devices appear automatically as the router reports them and are grouped beneath the gateway in the device registry.

The integration talks to the gateway locally and does not reach out to the UniFi cloud. Data is refreshed every five seconds through a single coordinated poll that feeds all entities.

## Troubleshooting

- `Invalid credentials` or `Access denied` errors mean the gateway rejected the login; verify the username/password and that the account still has API access.
- `Failed to connect` indicates Home Assistant cannot reach the HTTPS endpoint—check network connectivity or firewalls.
- If data stops updating after changing credentials on the gateway, remove the integration and add it again so a new session token is created.

## Project Structure

The repository follows the standard Home Assistant custom integration layout:

```
custom_components/ubiquiti_mobile/
├── __init__.py           # Set up the integration and forward platforms
├── api.py                # Async client for the router JSON-RPC endpoints
├── config_flow.py        # UI-driven configuration handler
├── const.py              # Domain constants and logger
├── coordinator.py        # DataUpdateCoordinator that polls the router
├── data.py               # Dataclasses shared between modules
├── device_tracker.py     # Client device tracker entities
├── entity.py             # Base entity with shared device info handling
├── model/                # Pydantic request/response models (uimqtt, session)
├── sensor.py             # Gateway sensors and per-client sensor entities
└── translations/         # Localised strings for the config flow/UI
```

Reference payloads live in `reference/`, and helper scripts for development sit in `scripts/`.

## Contributing

Problems, feature requests, or pull requests are welcome. See `CONTRIBUTING.md` for the recommended development workflow.
