# Installation

This guide covers the installation of Pontos and its dependencies.

## Prerequisites

Before installing Pontos, ensure you have:

- **Python 3.12** or higher
- **Git** with LFS support (for model weights)
- **Sentinel Hub Account** - Register at [Sentinel Hub](https://www.sentinel-hub.com/)

### GPU Support (Optional)

For GPU-accelerated inference:

- **NVIDIA GPUs**: CUDA 11.8+ with cuDNN
- **AMD GPUs**: ROCm 5.6+ (Linux only)

---

## Installation Methods

=== "pip (Recommended)"

    ```bash
    # Clone the repository
    git clone https://github.com/teyk0o/pontos.git
    cd pontos

    # Pull model weights (Git LFS)
    git lfs pull

    # Create virtual environment
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # or: venv\Scripts\activate  # Windows

    # Install package
    pip install -e .
    ```

=== "Docker"

    ```bash
    # Build the Docker image
    docker build -f docker/Dockerfile -t pontos:latest .

    # Verify installation
    docker run pontos:latest pontos --help
    ```

=== "From requirements.txt"

    ```bash
    # Clone and enter directory
    git clone https://github.com/teyk0o/pontos.git
    cd pontos

    # Pull model weights
    git lfs pull

    # Install dependencies
    pip install -r requirements.txt

    # Install package
    pip install -e .
    ```

---

## Verify Installation

After installation, verify that Pontos is correctly installed:

```bash
# Check CLI is available
pontos --help

# Check Python import
python -c "from pontos import VesselDetector; print('OK')"
```

Expected output for `pontos --help`:

```
Usage: pontos [OPTIONS] COMMAND [ARGS]...

  Pontos - AI-powered ship detection system

Options:
  --help  Show this message and exit.

Commands:
  scan  Scan satellite imagery for vessels
```

---

## Model Weights

Pontos uses a pre-trained YOLO11s model (`yolo11s_tci.pt`) stored via Git LFS.

!!! warning "Important"
    Make sure to run `git lfs pull` after cloning to download the model weights (~19MB).

Verify the model is correctly downloaded:

```bash
# Check file size (should be ~19MB, not a pointer)
ls -lh models/yolo11s_tci.pt

# The file should be larger than 1KB
# If it shows ~130 bytes, run: git lfs pull
```

---

## Sentinel Hub Configuration

Pontos requires Sentinel Hub API credentials to download satellite imagery.

### Step 1: Create Account

1. Go to [Sentinel Hub](https://www.sentinel-hub.com/)
2. Create a free account (includes trial credits)
3. Navigate to **Dashboard** > **User Settings** > **OAuth Clients**

### Step 2: Create OAuth Client

1. Click **Create New OAuth Client**
2. Name: `pontos` (or any name)
3. Grant Type: `Client Credentials`
4. Copy the **Client ID** and **Client Secret**

### Step 3: Configure Credentials

Create a `.env` file in the project root:

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env  # or your preferred editor
```

Add your credentials:

```bash title=".env"
SH_CLIENT_ID=your-client-id-here
SH_CLIENT_SECRET=your-client-secret-here
```

!!! tip "Security"
    Never commit `.env` to version control. It's already in `.gitignore`.

---

## GPU Configuration

### NVIDIA CUDA

For NVIDIA GPUs, ensure CUDA is installed and accessible:

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Check GPU name
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

### AMD ROCm

For AMD GPUs on Linux:

```bash
# Check ROCm availability
python -c "import torch; print(torch.cuda.is_available())"

# The Docker image includes ROCm 7.2 + PyTorch 2.7.1
docker run --device=/dev/kfd --device=/dev/dri pontos:latest
```

### CPU Fallback

If no GPU is available, Pontos automatically falls back to CPU inference:

```bash
# Force CPU mode
export DEVICE=cpu
pontos scan --bbox 5.85,43.08,6.05,43.18 --date-start 2026-01-01 --date-end 2026-01-31
```

---

## Dependencies

Pontos requires the following main dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| `ultralytics` | >=8.3.0 | YOLO11s framework |
| `torch` | latest | Deep learning |
| `sentinelhub` | >=3.9.0 | Sentinel Hub API |
| `numpy` | latest | Numerical computing |
| `pillow` | latest | Image processing |
| `click` | latest | CLI framework |
| `python-dotenv` | latest | Environment variables |

Full dependency list available in `requirements.txt`.

---

## Troubleshooting

??? question "Model file is only ~130 bytes"

    This means Git LFS didn't download the actual file. Run:
    ```bash
    git lfs install
    git lfs pull
    ```

??? question "ImportError: No module named 'pontos'"

    Make sure you installed the package:
    ```bash
    pip install -e .
    ```

??? question "CUDA not available"

    Check your PyTorch installation:
    ```bash
    pip uninstall torch
    pip install torch --index-url https://download.pytorch.org/whl/cu118
    ```

??? question "Sentinel Hub authentication error"

    Verify your credentials are correctly set:
    ```bash
    echo $SH_CLIENT_ID
    echo $SH_CLIENT_SECRET
    ```

---

## Next Steps

Once installed, proceed to the [Quick Start](quickstart.md) guide to run your first detection scan.
