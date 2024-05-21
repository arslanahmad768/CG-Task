FROM python:3.12.2-slim-bookworm

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PORT 8000

# Expose the port
EXPOSE $PORT

# # Use a shell form of CMD to ensure the Poetry environment is used
# CMD ["poetry", "run", "uvicorn", "codegrapher.main:app", "--host", "0.0.0.0", "--port", "8000"]
