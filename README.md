# Ubiquiti Mobile for Home Assistant

This custom integration authenticates against the local JSON-RPC interface of a Ubiquiti Mobile Gateway and exposes its status in Home Assistant. Once configured the integration polls the gateway every five seconds, surfaces network telemetry, and keeps GPS data in sync so you can build automations around connectivity and location.

## Features

- `Wan Ip Address` sensor reports the public address assigned to the gateway.
- `Lan Ip Address` sensor shows the LAN address being advertised to clients.
- `Data Usage` sensor tracks the total bytes transferred since the gateway's last reset.
- `Clients` sensor indicates the number of connected devices.
- `Location` device tracker publishes GPS coordinates (latitude/longitude) when available.

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
- After setup you will find the sensors and device tracker listed above under the new device, which is named using the gateway's MAC address and model.

The integration talks to the gateway locally and does not reach out to the UniFi cloud. Data is refreshed every five seconds through a single coordinated poll that feeds all entities.

## Troubleshooting

- `Invalid credentials` or `Access denied` errors mean the gateway rejected the login; verify the username/password and that the account still has API access.
- `Failed to connect` indicates Home Assistant cannot reach the HTTPS endpoint—check network connectivity or firewalls.
- If data stops updating after changing credentials on the gateway, remove the integration and add it again so a new session token is created.

## Contributing

Problems, feature requests, or pull requests are welcome. See `CONTRIBUTING.md` for the recommended development workflow.
