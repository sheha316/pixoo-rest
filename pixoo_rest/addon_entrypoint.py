import json
import os
import shutil

import requests

OPTIONS_PATH = '/data/options.json'
SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')

BUNDLED_COMPONENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'pixoo_rest')
INSTALLED_COMPONENT_DIR = '/config/custom_components/pixoo_rest'


def _component_version(component_dir: str) -> str | None:
    manifest_path = os.path.join(component_dir, 'manifest.json')

    if not os.path.exists(manifest_path):
        return None

    with open(manifest_path) as manifest_file:
        return json.load(manifest_file).get('version')


def _notify_via_supervisor(message: str) -> None:
    if not SUPERVISOR_TOKEN:
        return

    try:
        requests.post(
            'http://supervisor/core/api/services/persistent_notification/create',
            headers={'Authorization': f'Bearer {SUPERVISOR_TOKEN}'},
            json={
                'title': 'Pixoo REST',
                'message': message,
                'notification_id': 'pixoo_rest_integration',
            },
            timeout=10,
        )
    except requests.exceptions.RequestException:
        pass  # best-effort; the addon must keep working even if this fails


def install_integration() -> None:
    """Copy the bundled custom_components/pixoo_rest integration into /config
    so it can be set up from Settings > Devices & Services, without the user
    having to manually copy any files themselves."""
    if not os.path.isdir('/config'):
        return  # no /config mapped (e.g. running outside the HA add-on)

    bundled_version = _component_version(BUNDLED_COMPONENT_DIR)

    if bundled_version is None:
        return

    if _component_version(INSTALLED_COMPONENT_DIR) == bundled_version:
        return  # already up to date

    os.makedirs(os.path.dirname(INSTALLED_COMPONENT_DIR), exist_ok=True)
    shutil.rmtree(INSTALLED_COMPONENT_DIR, ignore_errors=True)
    shutil.copytree(BUNDLED_COMPONENT_DIR, INSTALLED_COMPONENT_DIR)

    _notify_via_supervisor(
        'The Pixoo REST integration was installed/updated in custom_components. '
        'Restart Home Assistant, then add it via Settings > Devices & Services > '
        'Add Integration > "Pixoo REST".'
    )


def main() -> None:
    if os.path.exists(OPTIONS_PATH):
        with open(OPTIONS_PATH) as options_file:
            options = json.load(options_file)

        for key, value in options.items():
            if value is not None:
                os.environ[key.upper()] = str(value)

    install_integration()

    os.execvp('uv', ['uv', 'run', 'fastapi', 'run', 'pixoo_rest'])


if __name__ == '__main__':
    main()
