# Rate Limited API Gateway

A production-ready, async API Gateway built with **FastAPI** and **Redis**.

This project implements a robust API Gateway with the following core features:
*   **Multi-Tenant Rate Limiting**: Token Bucket algorithm backed by Redis (Lua scripts).
*   **Intelligent Caching**: Caches upstream GET responses to reduce load.
*   **Authentication**: API Key-based authentication with tiered access (Free, Basic, Premium, Enterprise).
*   **Async Architecture**: Built on `FastAPI` and `httpx` for high performance.

## 🚀 Features

*   **Rate Limiting**:
    *   **Algorithm**: Token Bucket (Atomic Redis operations).
    *   **Granularity**: Per API Key.
    *   **Headers**: Returns standard `X-RateLimit-*` headers.
*   **Caching**:
    *   **Storage**: Redis.
    *   **Strategy**: Cache-aside for GET requests.
    *   **Serialization**: Automatic JSON handling.
*   **Architecture**:
    *   Modular design (`rate_limiter`, `cache`, `gateway`).
    *   Dependency Injection.
    *   Comprehensive Test Suite (`pytest`, `fakeredis`).

## 🛠️ Tech Stack

*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
*   **Database/Cache**: [Redis](https://redis.io/)
*   **HTTP Client**: [httpx](https://www.python-httpx.org/)
*   **Testing**: [pytest](https://docs.pytest.org/), [fakeredis](https://pypi.org/project/fakeredis/)
*   **Configuration**: [Pydantic Settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/)

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd rate-limited-api-gateway
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\Activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables**:
    Create a `.env` file (or use defaults):
    ```env
    REDIS_URL=redis://localhost:6379/0
    APP_NAME="Rate Limited API Gateway"
    DEBUG=True
    ```

## 🏃 Usage

1.  **Start Redis**:
    Ensure you have a Redis instance running locally on port 6379.

2.  **Run the Application**:
    
    **Option A: Local (Python)**
    ```bash
    uvicorn app.main:app --reload
    ```

    **Option B: Docker (Recommended)**
    ```bash
    docker-compose up --build
    ```

3.  **Make Requests**:

    *   **Health Check**:
        ```bash
        curl http://localhost:8000/health
        ```

    *   **Proxy Request (Premium User)**:
        ```bash
        curl http://localhost:8000/api/v1/test \
          -H "X-API-Key: premium_user"
        ```

    *   **Proxy Request (Free User)**:
        ```bash
        curl http://localhost:8000/api/v1/test \
          -H "X-API-Key: user_1"
        ```

## 🧪 Testing

Run the full test suite (Unit + Integration):

```bash
pytest
```

## 📂 Project Structure

```
.
├── app/
│   ├── cache/          # Caching Layer
│   ├── gateway/        # Router & Proxy Logic
│   ├── rate_limiter/   # Rate Limiting Logic
│   ├── config.py       # Configuration
│   ├── main.py         # App Entry Point
│   └── models.py       # Domain Models
├── tests/              # Test Suite
├── requirements.txt    # Dependencies
└── README.md           # Documentation
```
