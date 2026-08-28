import os
import json

OPTIONS_PATH = '/data/options.json'


def main() -> None:
    if os.path.exists(OPTIONS_PATH):
        with open(OPTIONS_PATH) as options_file:
            options = json.load(options_file)

        for key, value in options.items():
            if value is not None:
                os.environ[key.upper()] = str(value)

    os.execvp('uv', ['uv', 'run', 'fastapi', 'run', 'pixoo_rest'])


if __name__ == '__main__':
    main()
