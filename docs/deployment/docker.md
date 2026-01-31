# Docker Deployment

Pontos includes full Docker support for containerized deployment.

## Quick Start

```bash
# Build image
docker build -f docker/Dockerfile -t pontos:latest .

# Run scan
docker run --env-file .env pontos:latest \
  pontos scan --bbox 5.85,43.08,6.05,43.18 \
              --date-start 2026-01-01 \
              --date-end 2026-01-31
```

---

## Docker Images

### Build Production Image

```bash
# Build from project root
docker build -f docker/Dockerfile -t pontos:latest .

# Build with specific tag
docker build -f docker/Dockerfile -t pontos:1.0.0 .

# Build with build args
docker build -f docker/Dockerfile \
  --build-arg PYTHON_VERSION=3.12 \
  -t pontos:latest .
```

### Image Details

- **Base**: Python 3.12-slim
- **Size**: ~2GB (includes PyTorch)
- **Architecture**: Multi-stage build

---

## Running Containers

### Basic Run

```bash
# Show help
docker run pontos:latest pontos --help

# Run scan with environment file
docker run --env-file .env pontos:latest \
  pontos scan --bbox 5.85,43.08,6.05,43.18 \
              --date-start 2026-01-01 \
              --date-end 2026-01-31
```

### With Volumes

```bash
# Mount data and output directories
docker run -v $(pwd)/data:/app/data \
           -v $(pwd)/runs:/app/runs \
           --env-file .env \
           pontos:latest \
           pontos scan --bbox 5.85,43.08,6.05,43.18 \
                       --date-start 2026-01-01 \
                       --date-end 2026-01-31 \
                       --output /app/runs/vessels.geojson
```

### Interactive Shell

```bash
# Enter container shell
docker run -it --env-file .env pontos:latest /bin/bash

# Inside container
pontos --help
python -c "from pontos import VesselDetector; print('OK')"
```

---

## GPU Support

### AMD ROCm

The default Docker image includes ROCm support:

```bash
# Run with AMD GPU
docker run --device=/dev/kfd \
           --device=/dev/dri \
           --env-file .env \
           pontos:latest \
           pontos scan --bbox 5.85,43.08,6.05,43.18 \
                       --date-start 2026-01-01 \
                       --date-end 2026-01-31
```

### NVIDIA CUDA

For NVIDIA GPUs, use nvidia-docker:

```bash
# Run with NVIDIA GPU
docker run --gpus all \
           --env-file .env \
           pontos:latest \
           pontos scan --bbox 5.85,43.08,6.05,43.18 \
                       --date-start 2026-01-01 \
                       --date-end 2026-01-31
```

### Force CPU Mode

```bash
docker run -e DEVICE=cpu \
           --env-file .env \
           pontos:latest \
           pontos scan --bbox 5.85,43.08,6.05,43.18 \
                       --date-start 2026-01-01 \
                       --date-end 2026-01-31
```

---

## Docker Compose

### Production

```yaml title="docker-compose.yml"
services:
  pontos:
    build:
      context: .
      dockerfile: docker/Dockerfile
    environment:
      - SH_CLIENT_ID=${SH_CLIENT_ID}
      - SH_CLIENT_SECRET=${SH_CLIENT_SECRET}
      - DEVICE=cpu
      - CONFIDENCE_THRESHOLD=0.05
    volumes:
      - ./data:/app/data
      - ./runs:/app/runs
      - ultralytics_config:/app/.config/Ultralytics
    command: >
      pontos scan
      --bbox 5.85,43.08,6.05,43.18
      --date-start 2026-01-01
      --date-end 2026-01-31
      --output /app/runs/vessels.geojson

volumes:
  ultralytics_config:
```

```bash
# Run with docker-compose
docker-compose up
```

### Development

```yaml title="docker-compose.dev.yml"
services:
  pontos-dev:
    build:
      context: .
      dockerfile: docker/Dockerfile
    environment:
      - SH_CLIENT_ID=${SH_CLIENT_ID}
      - SH_CLIENT_SECRET=${SH_CLIENT_SECRET}
      - DEVICE=cpu
    volumes:
      - .:/app  # Mount source for hot reload
      - ./data:/app/data
      - ./runs:/app/runs
    stdin_open: true
    tty: true
    command: /bin/bash
```

```bash
# Start development container
docker-compose -f docker-compose.dev.yml up -d

# Enter container
docker-compose -f docker-compose.dev.yml exec pontos-dev bash

# Run tests inside container
pytest
```

---

## Dockerfile Structure

The Dockerfile uses multi-stage builds:

### Stage 1: Base

```dockerfile
FROM python:3.12-slim as base

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
```

### Stage 2: Dependencies

```dockerfile
FROM base as dependencies

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

### Stage 3: Application

```dockerfile
FROM dependencies as application

COPY . .
RUN pip install -e .

# Configure Ultralytics
ENV YOLO_CONFIG_DIR=/app/.config/Ultralytics

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pontos --help || exit 1

ENTRYPOINT ["pontos"]
CMD ["--help"]
```

---

## Environment Variables

Pass credentials and configuration:

```bash
# Using --env-file
docker run --env-file .env pontos:latest

# Using -e flags
docker run -e SH_CLIENT_ID=xxx \
           -e SH_CLIENT_SECRET=xxx \
           -e DEVICE=cpu \
           pontos:latest
```

**Available Variables:**

| Variable | Description |
|----------|-------------|
| `SH_CLIENT_ID` | Sentinel Hub Client ID |
| `SH_CLIENT_SECRET` | Sentinel Hub Client Secret |
| `DEVICE` | Computation device (`cpu`, `0`, `1`) |
| `CONFIDENCE_THRESHOLD` | Detection threshold |
| `MODEL_PATH` | Path to model weights |

---

## Health Checks

The container includes a health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pontos --help || exit 1
```

Check container health:

```bash
docker inspect --format='{{.State.Health.Status}}' <container_id>
```

---

## Volumes

### Data Volume

Store downloaded satellite imagery:

```bash
docker run -v /host/data:/app/data pontos:latest
```

### Runs Volume

Store detection outputs:

```bash
docker run -v /host/runs:/app/runs pontos:latest
```

### Model Cache

Persist Ultralytics model cache:

```bash
docker run -v ultralytics_cache:/app/.config/Ultralytics pontos:latest
```

---

## Container Registry

### Push to Docker Hub

```bash
# Tag image
docker tag pontos:latest username/pontos:latest

# Push
docker push username/pontos:latest
```

### Push to GitHub Container Registry

```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag
docker tag pontos:latest ghcr.io/teyk0o/pontos:latest

# Push
docker push ghcr.io/teyk0o/pontos:latest
```

---

## Troubleshooting

??? question "Container exits immediately"

    Check logs:
    ```bash
    docker logs <container_id>
    ```

??? question "Permission denied errors"

    Check volume permissions:
    ```bash
    docker run -u $(id -u):$(id -g) ...
    ```

??? question "GPU not detected"

    Verify GPU access:
    ```bash
    docker run --gpus all nvidia/cuda:11.8.0-base nvidia-smi
    ```

??? question "Out of memory"

    Limit memory usage:
    ```bash
    docker run --memory=4g pontos:latest
    ```

---

## Best Practices

1. **Use `.env` file** - Never hardcode credentials
2. **Mount volumes** - Persist data outside containers
3. **Use health checks** - Monitor container status
4. **Tag images** - Use semantic versioning
5. **Multi-stage builds** - Keep images small
6. **Non-root user** - Run as non-root when possible

---

## Next Steps

- [CI/CD](ci-cd.md) - Automated builds and tests
- [Configuration](../getting-started/configuration.md) - Configuration options
