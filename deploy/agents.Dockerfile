# Hidden Rent agents app (Fly): iMessage agent + onboarding page (Node 22) + ASI:One uAgent (py3.12 via uv) in one machine.
FROM node:22-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv
WORKDIR /app
COPY asi-agent/pyproject.toml asi-agent/uv.lock asi-agent/
RUN cd asi-agent && uv sync --frozen --no-dev
COPY agent/package.json agent/package-lock.json agent/
RUN cd agent && npm ci --no-audit --no-fund
COPY . .
ENV PYTHONUNBUFFERED=1 NODE_ENV=production
CMD ["bash", "deploy/agents-start.sh"]
