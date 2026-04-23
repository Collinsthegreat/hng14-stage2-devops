# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-alpine AS builder

WORKDIR /build

# Install build dependencies
# hadolint ignore=DL3018
RUN apk update && apk upgrade --no-cache && \
    apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.11-alpine AS runtime

WORKDIR /app

# Upgrades and Create non-root user
# hadolint ignore=DL3018
RUN apk update && apk upgrade --no-cache && \
    addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
