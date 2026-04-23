# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /build

COPY package*.json ./
RUN apk update && apk upgrade --no-cache && \
    npm ci --only=production

COPY . .

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM node:20-alpine AS runtime

WORKDIR /app

RUN apk update && apk upgrade --no-cache && \
    addgroup --gid 1001 appgroup && \
    adduser --uid 1001 --ingroup appgroup --shell /bin/sh --disabled-password appuser

COPY --from=builder --chown=appuser:appgroup /build/node_modules ./node_modules
COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD wget -qO- http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
