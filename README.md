# LedgerCore: A Distributed FinTech Engine

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis)
![Celery](https://img.shields.io/badge/Celery-37814A?logo=celery)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker)

## Description

LedgerCore is a highly concurrent, fully containerized financial backend engineered to process thousands of secure transactions without race conditions or data loss. Built with FastAPI, PostgreSQL, Redis, and Celery, this project strictly separates the API gateway from background processing to ensure maximum availability.

It features a strict `customers` and `employees` domain schema, Role-Based Access Control (RBAC), and custom idempotency middleware. In recent benchmarks, the distributed engine successfully processed a 500-user concurrent stress test via Locust, achieving a 0.0% failure rate while mitigating heavy database lock contention.

<br>
    <p align="center">
        <img src="architecture.jpg" alt="Project Architecture Overview">
    </p>
<br>

**Core Technologies:**
* **API Gateway:** Python, FastAPI, Uvicorn
* **Data Access:** PostgreSQL, SQLAlchemy (ORM), Alembic (Migrations)
* **Asynchronous Processing:** Celery, Redis (Message Broker & Idempotency Cache)
* **Testing & Infrastructure:** Locust, Docker, Docker Compose

## Motivation

Most entry-level backend APIs handle simple CRUD operations beautifully but completely fall apart under heavy transactional load. I built this system to actively solve the hardest problems in financial technology: preventing double-spending and managing deadlocks during high-concurrency traffic spikes.

By offloading heavy PostgreSQL row-level locks (`SELECT ... FOR UPDATE`) to an isolated Celery background worker, and implementing Redis as an idempotency shield at the network perimeter, I wanted to engineer a system that guarantees ACID compliance without sacrificing initial API response speeds.

## Quick Start

The entire distributed ecosystem is containerized. You can boot the API, database, cache, workers, and load testers locally in just a few commands.

**Prerequisites:**
* Git
* Docker & Docker Compose

**Installation & Boot:**
1. Clone the repository and navigate to the directory:
   ```bash
   git clone https://github.com/yourusername/fintech-ledger-api.git
   cd fintech-ledger-api
   ```
2. Boot the distributed Docker network in the background:
   ```bash
   docker compose up --build -d
   ```
3. Run the database migrations and inject the test data (including the `load_tester` account):
   ```bash
   docker compose exec api alembic upgrade head
   docker compose exec api python seed_money.py
   ```

## Usage

Once the containers are running, you can explore the API manually or launch the automated stress test.

**Interactive API Docs (Swagger UI):**
Navigate to `http://localhost:8000/docs` to view the endpoints. You can log in, generate a secure JWT, and manually trigger transfers between accounts to watch the background workers process the queue.

**Launching the Locust Swarm:**
To test the idempotency middleware and transaction locks under heavy load:
1. Open the Locust dashboard at `http://localhost:8089` in your browser.
2. Enter `500` for the number of peak concurrent users and `50` for the spawn rate.
3. Set the host to `http://api:8000` (Locust will route internally via Docker DNS).
4. Click "Start Swarming" and monitor the 0% failure rate as Uvicorn and Celery process the queue.

## Contributing

While this repository is primarily a personal portfolio piece, I actively welcome architectural reviews, optimizations, and discussions regarding distributed systems!

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/OptimizationName`).
3. Commit your changes (`git commit -m 'feat: implement new caching strategy'`).
4. Push to the branch (`git push origin feature/OptimizationName`).
5. Open a Pull Request detailing the tradeoffs and architectural decisions.
