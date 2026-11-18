# importing base image
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

# working directory and env variables setup
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_SYSTEM_PYTHON=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install dependencies 
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# copying application source code
COPY src/ ./src/
COPY main.py ./

# creating non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Exposing streamlit default port
EXPOSE 8501

# Built in healthcheck
HEALTHCHECK CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# start the app
ENTRYPOINT ["uv", "run", "streamlit", "run", "src/ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
