# Use Python 3.11 slim
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project metadata first
COPY pyproject.toml ./

# Install dependencies from pyproject.toml
RUN uv pip install --system requests python-dotenv supabase flask

# Copy application code
COPY whale_watcher.py app.py ./
COPY services/ ./services/

# Run the application
CMD ["python", "app.py"]
