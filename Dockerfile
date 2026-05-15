FROM python:3.14-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
ENV HOME=/opt/src/
WORKDIR $HOME

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# We use uv pip install to install directly into the system python
RUN uv pip install --system -r pyproject.toml

# Note: The source code is mounted as a volume in docker-compose.yaml
# but we set the WORKDIR and PYTHONPATH to ensure things run correctly.
ENV PYTHONPATH=$HOME
