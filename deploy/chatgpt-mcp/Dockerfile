FROM python:3.12-slim

ARG VULCA_VERSION=0.23.1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VULCA_REMOTE_MCP_TRANSPORT=streamable-http \
    VULCA_REMOTE_MCP_HOST=0.0.0.0 \
    VULCA_REMOTE_MCP_PATH=/mcp \
    VULCA_REMOTE_WORKSPACE_ROOT=/app/workspace

WORKDIR /app

RUN mkdir -p /app/workspace

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir "vulca[mcp]==${VULCA_VERSION}"

CMD ["sh", "-c", "VULCA_REMOTE_MCP_PORT=${PORT:-8765} vulca-mcp-remote"]
