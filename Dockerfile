# Using a lightweight Python base image
FROM python:3.12-slim

# Installing the uv package manager directly from Astral's Official Image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Setting the working directory inside the container
WORKDIR /app

# Copying the dependency files first (this caches the installation step)
COPY pyproject.toml uv.lock ./

# Installing dependencies using uv (creates a virtual environment inside /app/.venv)
RUN uv sync --frozen

# Copying the rest of the application code
COPY . .

# Placing the Virtual Environment in the system path so the command runs automatically
ENV PATH="/app/.venv/bin:$PATH"