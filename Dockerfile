FROM ghcr.io/astral-sh/uv:python3.14-trixie

ENV UV_NO_DEV=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install --yes --no-install-recommends curl

WORKDIR /usr/app

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --locked

COPY static static/
COPY pixoo_rest pixoo_rest/

HEALTHCHECK --interval=5m --timeout=3s \
    CMD curl --fail --silent http://localhost:8000/${SCRIPT_NAME}/health || exit 1

CMD [ "uv", "run", "python", "-m", "pixoo_rest.addon_entrypoint" ]
