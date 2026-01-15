
---

```md
# Autonomous Distributed Job Orchestration System

A backend system for **asynchronous, fault-tolerant job execution** using distributed workers, Redis queues, and PostgreSQL.  
Designed with **production-oriented reliability concepts** such as retries, crash recovery, rate limiting, idempotency, and real-time updates.

---

## 📌 Overview

This project allows clients to submit long-running jobs without blocking the API.  
Jobs are queued in Redis, processed by independent worker processes, and persisted in PostgreSQL as the source of truth.

The system is designed to handle:
- Worker crashes
- Duplicate job submissions
- Abuse via excessive requests
- Long-running or stuck jobs
- Safe shutdowns and restarts

---

## 🧱 High-Level Architecture

```

Client
│
▼
FastAPI (Auth, Rate Limiting, Idempotency)
│
▼
Redis Queue (BLPOP)
│
▼
Worker Processes
│
▼
PostgreSQL (Persistent Job State)

Redis Pub/Sub ──► WebSockets (Real-time Job Updates)

```

---

## ✨ Key Features

- Asynchronous job submission
- Distributed worker execution
- Redis-based job queue
- Persistent job state in PostgreSQL
- Automatic retries with limits
- Timeout & stuck-job detection
- Crash recovery on restart
- JWT-based authentication
- Per-user rate limiting
- Idempotent job submission
- Graceful worker shutdown
- Real-time job updates via WebSockets
- System metrics & observability

---

```

---

## 🔄 Job Lifecycle

```

QUEUED → RUNNING → COMPLETED
↘
FAILED → RETRYING → RUNNING

```

- Redis handles scheduling
- PostgreSQL tracks all job states
- Recovery logic re-queues stale RUNNING jobs

---

## 🔐 Authentication & Authorization

- JWT-based authentication
- Each job is associated with a user
- Users can only access their own jobs

---

## 🚦 Rate Limiting

- Per-user job submission limits
- Implemented using Redis counters with TTL
- Prevents queue flooding and abuse

---

## 🔁 Idempotency

- Supports `Idempotency-Key` request header
- Duplicate requests return the same `job_id`
- Prevents duplicate job execution during retries

---

## 🔄 Crash Recovery

- On API startup, stale RUNNING jobs are detected
- Such jobs are safely re-queued into Redis
- Ensures no job is permanently lost

---

## 📊 Metrics & Observability

Endpoint:
```

GET /metrics

```

Provides:
- Queue length
- Job counts by state
- Average execution latency
- Throughput (jobs per minute)

---

## 📡 Real-Time Updates

- Redis Pub/Sub broadcasts job state changes
- WebSocket clients receive live updates:
```

RUNNING → COMPLETED / FAILED

````

---

## ▶️ How to Run (Local)

### 1️⃣ Start Infrastructure
```bash
docker-compose up -d
````

### 2️⃣ Activate Virtual Environment

```bash
source venv/bin/activate
# or (Windows)
.\venv\Scripts\activate
```

### 3️⃣ Start API

```bash
uvicorn api.main:app --reload
```

### 4️⃣ Start Worker

```bash
python -m worker.worker
```

---

## 🔌 API Endpoints

| Method | Endpoint          | Description       |
| ------ | ----------------- | ----------------- |
| POST   | /jobs             | Submit a job      |
| GET    | /jobs/{job_id}    | Get job status    |
| GET    | /metrics          | System metrics    |
| WS     | /ws/jobs/{job_id} | Real-time updates |
| GET    | /health           | Health check      |

---

## 🛠️ Tech Stack

* **Language:** Python
* **Backend:** FastAPI, Uvicorn
* **Queue & Messaging:** Redis
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Real-Time:** WebSockets, Redis Pub/Sub
* **Security:** JWT Authentication
* **DevOps:** Docker, Docker Compose

---

## 🎯 Design Goals

* Reliability over complexity
* Clear separation of concerns
* Production-oriented backend design
* Safe handling of failures and retries

---

## 👤 Author

**Soumyajeet Saha**
Final-year Computer Science Engineering student
Focused on backend systems & distributed architectures

---

## 📄 License

This project is licensed under the **MIT License**.

```

---

### ✅ You are done

- This README is **resume-grade**
- **Interview-safe**
- **No overclaiming**
- Matches your **actual implementation**

You can now:
- Push to GitHub
- Add MIT `LICENSE` file
- Focus fully on **Java coding for placements**

If you ever want a **shorter README**, **portfolio version**, or **ATS-optimized summary**, just ask.
```
