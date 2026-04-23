# Bugs Found and Fixed

## Fix 1
- **File:** api/main.py
- **Line:** 8
- **Problem:** Redis host is hardcoded to `"localhost"`. Inside a Docker container, `localhost` refers to the container itself, not the Redis service. The API would fail to connect to Redis when running in Docker Compose since Redis runs in a separate container accessible via the service name `redis`.
- **Fix:** Changed to use the environment variable `os.environ.get("REDIS_HOST", "redis")` so the host is configurable and defaults to the Docker Compose service name `redis`.

## Fix 2
- **File:** api/main.py
- **Line:** 8
- **Problem:** Redis port is hardcoded to `6379` with no ability to override via environment variable. While 6379 is the default Redis port, hardcoding it violates the twelve-factor app methodology and prevents configuration changes without code modification.
- **Fix:** Changed to use the environment variable `int(os.environ.get("REDIS_PORT", 6379))` so the port is configurable via environment variables.

## Fix 3
- **File:** api/main.py
- **Line:** 8
- **Problem:** Redis client variable is named `r`, which is a non-descriptive single-letter variable name. More critically, the unit tests mock `main.redis_client` — if the variable is named `r`, the mock will not patch the correct object and all tests that depend on mocked Redis behavior will fail.
- **Fix:** Renamed the Redis client variable from `r` to `redis_client` to match the mock target in the test suite and improve code readability.

## Fix 4
- **File:** api/main.py
- **Line:** (missing entirely)
- **Problem:** No CORS (Cross-Origin Resource Sharing) middleware is configured. The frontend service runs on a different origin (port 3000) than the API (port 8000). Without CORS headers, the browser will block all cross-origin requests from the frontend to the API, making the entire system non-functional from a browser.
- **Fix:** Added `CORSMiddleware` from FastAPI with `allow_origins=["*"]`, `allow_methods=["*"]`, and `allow_headers=["*"]` to permit cross-origin requests from the frontend.

## Fix 5
- **File:** api/main.py
- **Line:** (missing entirely)
- **Problem:** No root `/` endpoint exists. This is expected by tests (`test_root_returns_200_and_json`) and is a standard practice for API services to provide a basic status/info response at the root path.
- **Fix:** Added a `GET /` endpoint that returns `{"message": "API is running"}` with a 200 status code.

## Fix 6
- **File:** api/main.py
- **Line:** (missing entirely)
- **Problem:** No `/health` endpoint exists. Docker HEALTHCHECK directives in the Dockerfile and docker-compose.yml rely on `GET /health` returning a 200 response. Without this endpoint, Docker will mark the container as unhealthy, causing `depends_on` with `condition: service_healthy` to block dependent services from starting indefinitely.
- **Fix:** Added a `GET /health` endpoint that pings Redis to verify connectivity and returns `{"message": "healthy"}` with a 200 status code, or raises a 503 error if Redis is unavailable.

## Fix 7
- **File:** api/main.py
- **Line:** 11
- **Problem:** The `create_job()` function accepts no request body parameters. The unit test sends `json={"task": "test-task"}` and the integration test sends `{"task": "integration-test-job"}`. Without accepting this body, the task data is silently ignored, and FastAPI may reject the request or not process it correctly.
- **Fix:** Added a Pydantic `JobRequest` model with a `task` field (defaulting to `"default"`) and updated the endpoint to accept it as a request body parameter.

## Fix 8
- **File:** api/main.py
- **Line:** 14
- **Problem:** Job initial status is set to `"queued"` but the test expects `"pending"` (`mock_r.get.return_value = b'{"status": "pending", ...}'`). The frontend polls for status and expects the lifecycle `pending → processing → completed`. Using `"queued"` breaks the expected status flow.
- **Fix:** Changed initial job status from `"queued"` to `"pending"` to match the expected status lifecycle.

## Fix 9
- **File:** api/main.py
- **Line:** 13-14
- **Problem:** Uses `redis.hset()` and `redis.hget()` (Redis hash operations) for job storage, but the test fixture mocks `redis_client.get()` and `redis_client.set()` (simple key-value operations). The mock `mock_r.get.return_value = b'{"status": "pending", "job_id": "test-123"}'` expects JSON-serialized data via `get()`, not hash fields via `hget()`. This mismatch causes all tests to fail.
- **Fix:** Changed job storage to use `redis_client.set()` with JSON-serialized data and `redis_client.get()` for retrieval, matching the test expectations and providing a cleaner serialization format.

## Fix 10
- **File:** api/main.py
- **Line:** 13
- **Problem:** Redis queue name is `"job"` (singular). While this technically works if the worker uses the same name, it's inconsistent with the REST endpoint naming convention (`/jobs` plural) and should be standardized to `"jobs"` for clarity and consistency.
- **Fix:** Changed queue name from `"job"` to `"jobs"` to match the endpoint naming convention. Updated worker to use the same queue name.

## Fix 11
- **File:** api/main.py
- **Line:** 20-21
- **Problem:** When a job is not found, the API returns HTTP 200 with `{"error": "not found"}` instead of HTTP 404. This violates REST conventions — a missing resource should return 404. The test `test_invalid_job_id_returns_404_or_json` checks for `status_code in (404, 200)` but properly returning 404 is the correct behavior.
- **Fix:** Changed to raise `HTTPException(status_code=404, detail="Job not found")` when a job ID is not found in Redis, returning proper HTTP 404 status.

## Fix 12
- **File:** api/main.py
- **Line:** (missing entirely)
- **Problem:** No error handling exists for Redis connection failures. If Redis is temporarily unavailable (e.g., during startup or network issues), any endpoint call would raise an unhandled `redis.exceptions.ConnectionError`, causing a 500 Internal Server Error with a stack trace.
- **Fix:** Added try/except handling in the `/health` endpoint to catch Redis connection errors and return a proper 503 Service Unavailable response. The Redis client's lazy connection and retry mechanisms handle transient failures for other endpoints.

## Fix 13
- **File:** api/.env
- **Line:** 1
- **Problem:** The file contains a hardcoded secret `REDIS_PASSWORD=supersecretpassword123` and is committed to the git repository. This is a critical security vulnerability — secrets in version control can be extracted by anyone with repository access and persist in git history even after deletion.
- **Fix:** Deleted `api/.env` from the repository and git history. Added `.env` patterns to `.gitignore` to prevent future accidental commits. Created `.env.example` with placeholder values for documentation.

## Fix 14
- **File:** api/requirements.txt
- **Line:** (missing entries)
- **Problem:** Missing test dependencies `pytest`, `pytest-cov`, and `httpx`. Without `pytest` and `pytest-cov`, the test suite cannot run. Without `httpx`, FastAPI's `TestClient` will fail with an import error since `httpx` is the underlying HTTP client used by Starlette's test client.
- **Fix:** Added `pytest`, `pytest-cov`, and `httpx` to `api/requirements.txt`.

## Fix 15
- **File:** worker/worker.py
- **Line:** 6
- **Problem:** Redis host is hardcoded to `"localhost"`. Same issue as Fix 1 — inside Docker, `localhost` refers to the worker container itself, not the Redis service container. The worker would fail to connect to Redis.
- **Fix:** Changed to `os.environ.get("REDIS_HOST", "redis")` to use the Docker Compose service name by default.

## Fix 16
- **File:** worker/worker.py
- **Line:** 6
- **Problem:** Redis port is hardcoded to `6379` with no environment variable override capability.
- **Fix:** Changed to `int(os.environ.get("REDIS_PORT", 6379))` to allow configuration via environment variable.

## Fix 17
- **File:** worker/worker.py
- **Line:** 4, 14-18
- **Problem:** The `signal` module is imported on line 4 but never used. The worker runs an infinite `while True` loop with no way to shut down gracefully. When Docker sends SIGTERM during container stop, the process is forcefully killed after the timeout period, potentially interrupting in-progress job processing.
- **Fix:** Implemented graceful shutdown by registering signal handlers for SIGTERM and SIGINT that set a `shutdown` flag. Changed `while True` to `while not shutdown` so the worker finishes its current job before exiting cleanly.

## Fix 18
- **File:** worker/worker.py
- **Line:** 9-12
- **Problem:** Job processing jumps directly from initial status to `"completed"` without ever setting `"processing"`. The expected status lifecycle is `pending → processing → completed`. Without the `"processing"` state, the frontend cannot show real-time progress and there is no way to distinguish between a pending job and one actively being worked on.
- **Fix:** Added `redis_client.set(f"job:{job_id}", json.dumps({"job_id": job_id, "status": "processing"}))` before the simulated work begins, then sets `"completed"` after work finishes.

## Fix 19
- **File:** worker/worker.py
- **Line:** 14-18
- **Problem:** No error handling in the main loop or job processing function. If Redis becomes temporarily unavailable or a job processing error occurs, the worker crashes with an unhandled exception and the container exits. Docker `restart: always` would restart it, but any in-progress job would be lost with no status update.
- **Fix:** Added try/except around the main loop's Redis operations (catching `redis.exceptions.ConnectionError` with a 5-second retry delay) and around job processing (setting status to `"failed"` on error). This prevents crashes and provides proper error status tracking.

## Fix 20
- **File:** worker/worker.py
- **Line:** 15
- **Problem:** Queue name `"job"` must match the API's queue name. After Fix 10, the API uses `"jobs"`. If the queue names don't match, the worker will never receive any jobs — it would block forever on an empty queue while jobs pile up in a different queue.
- **Fix:** Changed `brpop("job", ...)` to `brpop("jobs", ...)` to match the API's queue name.

## Fix 21
- **File:** worker/worker.py
- **Line:** 11
- **Problem:** Uses `redis.hset()` for status updates, but the API now uses `redis.set()` with JSON serialization (Fix 9). If the worker writes with `hset` but the API reads with `get`, the API will never see the worker's status updates — `get` returns the old JSON blob while `hset` updates a completely different data structure (hash vs string).
- **Fix:** Changed worker to use `redis_client.set()` with `json.dumps()` for status updates, matching the API's data storage pattern.

## Fix 22
- **File:** frontend/app.js
- **Line:** 6
- **Problem:** `API_URL` is hardcoded to `"http://localhost:8000"`. Inside a Docker container, `localhost` refers to the frontend container itself, not the API service. All proxy requests from the frontend to the API would fail with connection refused.
- **Fix:** Changed to `process.env.API_URL || 'http://api:8000'` to use the Docker Compose service name by default and allow override via environment variable.

## Fix 23
- **File:** frontend/app.js
- **Line:** 29
- **Problem:** Server port is hardcoded to `3000` with no environment variable override. This prevents runtime configuration and violates twelve-factor app methodology.
- **Fix:** Changed to `parseInt(process.env.FRONTEND_PORT || '3000', 10)` to read the port from the `FRONTEND_PORT` environment variable.

## Fix 24
- **File:** frontend/app.js
- **Line:** 29
- **Problem:** `app.listen(3000)` binds to `localhost` (127.0.0.1) by default in Node.js. Inside a Docker container, this means the server is only accessible from within the container itself. External requests (from Docker's port forwarding, other containers, or Nginx) cannot reach the server.
- **Fix:** Changed to `app.listen(PORT, '0.0.0.0', ...)` to bind to all interfaces, making the server accessible from outside the container.

## Fix 25
- **File:** frontend/app.js
- **Line:** (missing entirely)
- **Problem:** No `/health` endpoint exists. The Docker HEALTHCHECK in the Dockerfile uses `wget -qO- http://localhost:3000/` which would serve the static HTML file. However, a dedicated health endpoint is needed for explicit health monitoring and the docker-compose healthcheck.
- **Fix:** Added a `GET /health` endpoint returning `{"message": "healthy"}` for Docker healthcheck and monitoring.

## Fix 26
- **File:** frontend/app.js
- **Line:** 13
- **Problem:** The `POST /submit` handler calls `axios.post(\`${API_URL}/jobs\`)` without forwarding the request body. Any task data sent by the client is silently dropped. The API's `create_job` endpoint expects a JSON body with a `task` field.
- **Fix:** Changed to `axios.post(\`${API_URL}/jobs\`, req.body || {})` to forward the client's request body to the API.

## Fix 27
- **File:** frontend/app.js
- **Line:** (filename)
- **Problem:** The file is named `app.js` but the Dockerfile's CMD directive expects `server.js` (`CMD ["node", "server.js"]`). The container would crash immediately on startup with `Error: Cannot find module '/app/server.js'`.
- **Fix:** Renamed the file from `app.js` to `server.js` and updated `package.json` references accordingly.

## Fix 28
- **File:** frontend/package.json
- **Line:** 4, 6
- **Problem:** The `main` field points to `"app.js"` and the start script runs `"node app.js"`, but the file has been renamed to `server.js` (Fix 27). Running `npm start` would fail with a module not found error.
- **Fix:** Updated `main` to `"server.js"` and start script to `"node server.js"`.
