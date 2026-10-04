# Hidden Rent API app (Fly): P1 model server (py3.14, exact training pins) + FastAPI API (py3.12 via uv) in one machine.
# Build context = staging dir from deploy/stage.sh api (repo + trained model files + data/ caches).
FROM python:3.14.6-slim
# libgomp1: lightgbm/xgboost; libexpat1: rasterio's bundled GDAL.
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libexpat1 curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv
WORKDIR /app
COPY deploy/model-requirements.txt deploy/
RUN pip install --no-cache-dir -r deploy/model-requirements.txt
COPY api/pyproject.toml api/uv.lock api/
RUN cd api && uv sync --frozen --no-dev
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["bash", "deploy/api-start.sh"]
