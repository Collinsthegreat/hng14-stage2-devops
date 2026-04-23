import redis
import time
import os
import signal
import json

# Redis connection using environment variables
redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", 6379))
)

# Graceful shutdown handling
shutdown = False


def handle_signal(signum, frame):
    global shutdown
    print(f"Received signal {signum}, shutting down gracefully...")
    shutdown = True


signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)


def process_job(job_id):
    try:
        print(f"Processing job {job_id}")
        # Update status to processing
        redis_client.set(
            f"job:{job_id}",
            json.dumps({"job_id": job_id, "status": "processing"})
        )
        time.sleep(2)  # simulate work
        # Update status to completed
        redis_client.set(
            f"job:{job_id}",
            json.dumps({"job_id": job_id, "status": "completed"})
        )
        print(f"Done: {job_id}")
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        try:
            redis_client.set(
                f"job:{job_id}",
                json.dumps({"job_id": job_id, "status": "failed"})
            )
        except Exception:
            pass


def main():
    print("Worker started, waiting for jobs...")
    while not shutdown:
        try:
            job = redis_client.brpop("jobs", timeout=5)
            if job:
                _, job_id = job
                process_job(job_id.decode())
        except redis.exceptions.ConnectionError as e:
            print(f"Redis connection error: {e}, retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)
    print("Worker shutdown complete")


if __name__ == "__main__":
    main()