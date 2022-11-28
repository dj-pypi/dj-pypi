# syntax=docker/dockerfile:1

FROM python:3.11-slim

ARG USERNAME=code
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ENV PYTHONUNBUFFERED=1
# ENV GUNICORN_CMD_ARGS="--bind 0.0.0.0:8000 --workers 4 --worker-class=uvicorn.workers.UvicornWorker"
ENV DJANGO_SETTINGS_FILE=dj_pypi.settings
ENV DJANGO_DEBUG=""
ENV BASE_URL="http://localhost:8000"
ENV DATA_DIR=/data

COPY docker/initscript.sh /
COPY requirements.txt /app/

ENTRYPOINT ["/initscript.sh"]

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID --shell /bin/bash -m $USERNAME \
    && mkdir -p /data/static && chown -R $USER_UID:$USER_GID /data \
    && rm -rf /var/lib/apt/lists/

WORKDIR /app

RUN python -m pip install -r requirements.txt && rm -rf ~/.cache ~/.local

COPY . /app

VOLUME /app
VOLUME /data

EXPOSE 8000

USER $USERNAME

# CMD ["gunicorn", "dj_pypi.asgi:application"]
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--access-log", "dj_pypi.asgi:application"]
