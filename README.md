# 🏦 Zorvyn Finance API: Secure Records & Analytics Engine

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite)
![Security](https://img.shields.io/badge/Security-pyJWT%20%7C%20bcrypt-brightgreen)

## Description

Managing financial data requires a backend architecture that is not only logically sound but heavily fortified against edge-case vulnerabilities and performance bottlenecks. To meet the demanding requirements of modern FinTech infrastructure, I developed this robust FastAPI service centered around secure data modeling, strict Role-Based Access Control (RBAC), and efficient server-side data processing. 

I engineered a clean, multi-layered architecture that strictly separates API routing, security middleware, business logic, and database operations. Recognizing the vulnerabilities inherent in cryptographic algorithms, I implemented a strict Pydantic validation gateway to prevent `bcrypt` DoS attacks by capping payload sizes at the network perimeter. Furthermore, to ensure high-speed read operations across the API, I designed an O(1) stateless JWT dependency. This bypasses expensive database lookups by validating users via cryptographic signatures, demonstrating my ability to build highly scalable, defensive, and production-ready backend systems.

## Motivation

This project was built as a comprehensive backend assessment for Zorvyn FinTech. My primary motivation was to go beyond basic CRUD operations and demonstrate a senior-level understanding of system design tradeoffs, resource management, and clean coding principles. 

Instead of relying on client-side processing or memory-heavy ORM loops, I leveraged native SQLAlchemy aggregations (`func.sum()`) to offload dashboard analytics directly to the highly-optimized database engine. Coupled with custom timing attack mitigations in the authentication layer and strict literal typing for data integrity, this application serves as a showcase of my readiness to write maintainable, highly secure Python code that protects both user data and server infrastructure.

## Quick Start

This project utilizes `uv` for exceptionally fast dependency management and environment setup, though standard `pip` is fully supported.

**1. Clone the repository:**
```bash
git clone [https://github.com/yourusername/zorvyn.git](https://github.com/yourusername/zorvyn.git)
cd zorvyn
```

**2. Install dependencies:**
Using `uv` (recommended):
```bash
uv sync
```
*(Alternatively, use standard pip: `pip install fastapi uvicorn sqlalchemy pydantic passlib bcrypt pyjwt`)*

**3. Start the Application:**
Launch the Uvicorn ASGI server with the reload flag for development:
```bash
uv run uvicorn app.main:app --reload
```
*(The SQLite database `zorvyn.db` will automatically initialize on the first run).*

## Usage

Once the server is running, FastAPI automatically generates interactive documentation. You can view the endpoints, authenticate, and test the API directly via:
* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`

**Access Control Levels:**
The API enforces strict RBAC across its endpoints. You must register a user and authenticate via the Swagger UI padlock to receive a JWT Bearer token.
* **Viewer:** Read-only access to standard API metadata.
* **Analyst:** Granted read-access to the `GET /api/v1/records/` and `GET /api/v1/analytics/summary` endpoints.
* **Admin:** Full CRUD privileges, including the ability to `POST`, `PUT`, and `DELETE` financial records.

**Pagination Feature:**
The records listing endpoint supports query parameters for optimized database querying (e.g., `/api/v1/records/?skip=0&limit=50`).

## Contributing

While this repository is primarily a fixed assessment submission, standard contribution workflows apply for future architectural reviews:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/OptimizationName`).
3. Commit your changes (`git commit -m 'refactor: implement Redis caching for analytics'`).
4. Push to the branch (`git push origin feature/OptimizationName`).
5. Open a Pull Request detailing the tradeoffs and architectural decisions.