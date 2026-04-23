#!/usr/bin/env bash
# integration.sh — Full stack integration test
# Usage: ./integration.sh
# Brings up the full stack, submits a job via the frontend,
# polls until it completes, then tears everything down.

set -euo pipefail

TIMEOUT=60
FRONTEND_URL="http://localhost:3000"
API_URL="http://localhost:8000"

echo "=== Starting full stack integration test ==="

# Ensure clean state
docker compose down -v --remove-orphans 2>/dev/null || true

# Build and start all services
docker compose up -d --build
echo "Waiting for services to become healthy..."
sleep 30

# Wait for frontend
echo "Waiting for frontend..."
ELAPSED=0
until curl -sf "${FRONTEND_URL}/" > /dev/null; do
  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "ERROR: Frontend did not become ready within ${TIMEOUT}s"
    docker compose logs frontend
    docker compose down -v --remove-orphans
    exit 1
  fi
  sleep 5
  ELAPSED=$((ELAPSED + 5))
done
echo "Frontend is up"

# Wait for API
echo "Waiting for API..."
ELAPSED=0
until curl -sf "${API_URL}/health" > /dev/null; do
  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "ERROR: API did not become ready within ${TIMEOUT}s"
    docker compose logs api
    docker compose down -v --remove-orphans
    exit 1
  fi
  sleep 5
  ELAPSED=$((ELAPSED + 5))
done
echo "API is up"

# Submit a job via the frontend
echo "Submitting job via frontend /submit..."
RESPONSE=$(curl -sf -X POST "${FRONTEND_URL}/submit" \
  -H "Content-Type: application/json" \
  -d '{"task": "integration-test"}')
echo "Response: ${RESPONSE}"

JOB_ID=$(echo "${RESPONSE}" | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo "Job ID: ${JOB_ID}"

# Poll for completion with timeout
echo "Polling for job completion (timeout: ${TIMEOUT}s)..."
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
  STATUS_RESPONSE=$(curl -sf "${API_URL}/jobs/${JOB_ID}")
  STATUS=$(echo "${STATUS_RESPONSE}" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
  echo "  [${ELAPSED}s] status=${STATUS}"
  if [ "${STATUS}" = "completed" ]; then
    echo "=== Integration test PASSED — job completed successfully ==="
    docker compose down -v --remove-orphans
    exit 0
  fi
  sleep 5
  ELAPSED=$((ELAPSED + 5))
done

echo "ERROR: Job did not complete within ${TIMEOUT}s"
docker compose logs worker
docker compose down -v --remove-orphans
exit 1
