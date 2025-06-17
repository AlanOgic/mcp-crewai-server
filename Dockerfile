# MCP CrewAI Server - Production Dockerfile
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml .
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/mcpuser/.local/bin:$PATH" \
    MCP_SERVER_HOST=0.0.0.0 \
    MCP_SERVER_PORT=8765 \
    LOG_LEVEL=INFO

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Create app directory and data directory
WORKDIR /app
RUN mkdir -p /app/data /app/logs /app/certs && \
    chown -R mcpuser:mcpuser /app

# Copy application from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src /app/src

# Copy configuration files
COPY .env.template /app/.env.template
COPY docker/ /app/docker/
COPY start_http.py /app/start_http.py

# Set proper permissions
RUN chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8765/health || exit 1

# Expose port
EXPOSE 8765

# Add labels
LABEL maintainer="MCP CrewAI Team" \
      version="1.0.0" \
      description="Revolutionary MCP CrewAI Server with Autonomous Evolution"

# Default command - use HTTP server for better container support
CMD ["python", "/app/start_http.py"]