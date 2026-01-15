# Autonomous Distributed Job Orchestration System

## Overview
Backend system for executing long-running jobs asynchronously using Redis, PostgreSQL, and worker processes.

## Architecture
Client → FastAPI → Redis Queue → Worker → PostgreSQL  
Redis Pub/Sub → WebSockets (real-time updates)

## Features
- Asynchronous job execution
- Retry & timeout handling
- Crash recovery
- Real-time WebSocket updates
- JWT-based authentication
- Rate limiting
- Idempotent job submission
- Graceful shutdown

## Tech Stack
- FastAPI
- Redis (Queue + Pub/Sub)
- PostgreSQL
- Docker & Docker Compose

## How to Run
1. Start Redis & PostgreSQL
2. Start API: `uvicorn api.main:app`
3. Start worker: `py -m worker.worker`

## API Endpoints
- POST /jobs
- GET /jobs/{id}
- GET /metrics
- WS /ws/jobs/{id}

## Failure Handling
- Worker crash recovery
- Stale job detection
- Retry with limits

## Author
Soumyajeet Saha
