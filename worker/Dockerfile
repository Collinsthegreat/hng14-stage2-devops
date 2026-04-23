# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-alpine AS builder

WORKDIR /build

# hadolint ignore=DL3018
RUN apk update && apk upgrade --no-cache && \
    apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.11-alpine AS runtime

WORKDIR /app

# hadolint ignore=DL3018
RUN apk update && apk upgrade --no-cache && \
    addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

COPY --from=builder /install /usr/local
COPY --chown=appuser:appgroup . .

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import os, redis; r = redis.Redis(host=os.environ.get('REDIS_HOST','redis'), port=int(os.environ.get('REDIS_PORT','6379'))); r.ping()" || exit 1

CMD ["python", "worker.py"]
