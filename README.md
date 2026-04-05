# 🏦 Fintech Ledger API: Secure Records & Analytics Engine

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite)
![Security](https://img.shields.io/badge/Security-pyJWT%20%7C%20bcrypt-brightgreen)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

## Description

Managing financial data requires a backend architecture that is logically sound and fortified against vulnerabilities and performance bottlenecks. To meet standard FinTech requirements, I developed this FastAPI service centered around secure data modeling, strict Role-Based Access Control (RBAC), and efficient server-side data processing. 

I engineered a clean, multi-layered architecture that strictly separates API routing, security middleware, business logic, and database operations. Recognizing vulnerabilities in cryptographic algorithms, I implemented a strict Pydantic validation gateway to prevent `bcrypt` DoS attacks by capping payload sizes at the network perimeter. Furthermore, to ensure high-speed read operations across the API, I designed an O(1) stateless JWT dependency, which bypasses expensive database lookups by validating users via cryptographic signatures.

### 📊 Advanced Data Operations
* **Dynamic Search Engine:** The records endpoint supports dynamic, multi-parameter querying (exact type matches, fuzzy category text matching, and strict numerical boundaries) using RESTful query parameters.
* **High-Performance Analytics:** Instead of relying on memory-heavy Python loops, the dashboard endpoint offloads complex mathematical operations (Transaction Velocity, Average Transaction Value, and Outlier Detection) directly to the SQLite C-engine via SQLAlchemy groupings. All responses are strictly typed using nested Data Transfer Object (DTO) schemas.

> Make sure to take a look at the documentation after starting the app at this link: [Documentation](http://localhost:8000/redoc)

## Motivation

This project was built as a comprehensive backend assessment. My primary motivation was to go beyond basic CRUD operations and demonstrate a strong foundational understanding of system design tradeoffs, resource management, and clean coding principles. 

To prove the stability of this architecture, I engineered a highly isolated Pytest integration suite utilizing dependency overrides and automated in-memory (`sqlite:///:memory:`) database fixtures. This application serves as a showcase of my readiness to write maintainable, secure Python code that protects both user data and server infrastructure.

## Quick Start

This project utilizes `uv` for exceptionally fast dependency management and environment setup, though standard `pip` is fully supported.

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/fintech-ledger-api
cd fintech-ledger-api
```

**2. Install dependencies:**
Using `uv` (recommended):
```bash
uv sync
```
*(Alternatively, use standard pip: `pip install fastapi uvicorn sqlalchemy pydantic passlib bcrypt pyjwt pytest httpx`)*

**3. Start the Application:**
Launch the Uvicorn ASGI server with the reload flag for development:
```bash
uv run uvicorn app.main:app --reload
```
*(The SQLite database `ledger.db` will automatically initialize on the first run).*

## Usage & API Documentation

Once the server is running, FastAPI automatically generates interactive documentation. You can view the endpoints, authenticate, and test the API directly via:
* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`

**Access Control Levels:**
The API enforces strict RBAC across its endpoints. You must register a user and authenticate via the Swagger UI padlock to receive a JWT Bearer token.
* **Viewer:** Read-only access to standard API metadata.
* **Analyst:** Granted read-access to the `GET /api/v1/records/` and `GET /api/v1/analytics/summary` endpoints.
* **Admin:** Full CRUD privileges, including the ability to `POST`, `PUT`, and `DELETE` financial records, as well as User Management.

**Filtering & Pagination Feature:**
The records listing endpoint supports query parameters for optimized database querying and filtering (e.g., `/api/v1/records/?skip=0&limit=50&record_type=expense&category=Housing&min_amount=500`).

## Testing

The project includes a fully isolated integration test suite that tests authentication, validation, and database operations without polluting the local development database.
```bash
uv run pytest
```

## Contributing

While this repository is primarily a fixed assessment submission, standard contribution workflows apply for future architectural reviews:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/OptimizationName`).
3. Commit your changes (`git commit -m 'refactor: implement Redis caching for analytics'`).
4. Push to the branch (`git push origin feature/OptimizationName`).
5. Open a Pull Request detailing the tradeoffs and architectural decisions.
