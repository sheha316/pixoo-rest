# Pixoo REST

A RESTful API to easily interact with your Wi-Fi enabled Divoom Pixoo device, with a
built-in Swagger UI for drawing, sending images/GIFs, and controlling device settings
from your own automations.

## Configuration

| Option | Description |
|---|---|
| `PIXOO_HOST` | Hostname or IP address of your Pixoo device (mandatory). |
| `PIXOO_SCREEN_SIZE` | Screen size of your Pixoo device. Defaults to `64`. |
| `PIXOO_DEBUG` | Enable debug mode for the underlying Pixoo library. |
| `PIXOO_CONNECTION_CHECK` | Check the connection to the Pixoo device on startup. |
| `PIXOO_CONNECTION_CHECK_RETRIES` | Number of connection retries on startup. |
| `PIXOO_REST_DEBUG` | Enable debug mode for the REST app itself. |

## Usage

Once started, click "Open Web UI" (or go to `http://<your-ha-host>:8000/docs`) to
open the Swagger UI. Every request there also shows a ready-to-use `curl` command,
handy for reuse in Home Assistant `rest_command:` entries or shell scripts.

See the [full project README](https://github.com/sheha316/pixoo-rest) for more
details and examples.
