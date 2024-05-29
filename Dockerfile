# Use Python 3.12.2 slim image as base
FROM python:3.12.2-slim-bookworm AS builder

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock./

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi --no-cache-dir

# Multi-stage build: Start a new stage for the final image
FROM python:3.12.2-slim-bookworm

# Set working directory
WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PORT 8000

# Expose the port
EXPOSE $PORT

# Use a shell form of CMD to ensure the Poetry environment is used
CMD ["poetry", "run", "uvicorn", "codegrapher.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
