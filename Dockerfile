FROM python:3.12-slim AS builder

WORKDIR /build

ARG DEBIAN_FRONTEND=noninteractive

# Setup env variables
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync

FROM python:3.12-slim

ARG DEBIAN_FRONTEND=noninteractive

# Setup env variables
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl=7.* \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash rat
USER rat

WORKDIR /app

COPY --chown=rat --from=builder /build/.venv .venv

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s CMD curl -f http://localhost:8000/health/ || exit 1

ENTRYPOINT [".venv/bin/gunicorn", "rat.wsgi:application"]
CMD ["--bind", "0.0.0.0:8000"]