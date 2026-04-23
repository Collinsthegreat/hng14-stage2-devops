from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import uuid
import os
import json

app = FastAPI()

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection using environment variables
redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", 6379))
)


class JobRequest(BaseModel):
    task: str = "default"


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/health")
def health():
    try:
        redis_client.ping()
    except Exception:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    return {"message": "healthy"}


@app.post("/jobs", status_code=201)
def create_job(job: JobRequest):
    job_id = str(uuid.uuid4())
    redis_client.lpush("jobs", job_id)
    redis_client.set(
        f"job:{job_id}",
        json.dumps({"job_id": job_id, "status": "pending", "task": job.task})
    )
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    data = redis_client.get(f"job:{job_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    job_data = json.loads(data.decode())
    return {"job_id": job_id, "status": job_data["status"]}
