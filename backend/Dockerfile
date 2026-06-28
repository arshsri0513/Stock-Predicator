# Production Dockerfile for the FastAPI backend.
#
# Why a multi-stage-style approach with a slim base image: our dependency
# list (TensorFlow, PyTorch, scikit-learn) is large. Using python:3.12-slim
# instead of the full python:3.12 image saves real space (the full image
# bundles build tools and docs we don't need at runtime), which matters
# directly for free-tier deployment limits.

FROM python:3.12-slim

# Prevents Python from writing .pyc files and buffering stdout -- both
# matter for container logs: unbuffered output means logs appear in
# real-time in Render's dashboard rather than being held back.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed to build psycopg2 and other
# packages with native extensions. --no-install-recommends keeps the
# image smaller by skipping suggested-but-not-required packages.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements FIRST, before the rest of the code. Docker caches
# each instruction as a "layer" -- if only our application code changes
# (which happens constantly) but requirements.txt doesn't, Docker reuses
# the cached pip install layer instead of re-running it, making rebuilds
# much faster during development.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the actual application code
COPY . .

# Render (and most platforms) provide the actual port via the $PORT
# environment variable at runtime -- we can't hardcode 8000 here, since
# the platform decides which port to actually expose.
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
