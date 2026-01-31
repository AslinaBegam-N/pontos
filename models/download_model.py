"""Download YOLO11s marine vessel detection model from HuggingFace."""
import hashlib
import sys
from pathlib import Path
from urllib.request import urlretrieve
from urllib.error import URLError


# Model configuration
MODEL_URL = "https://huggingface.co/mayrajeo/marine-vessel-yolo/resolve/main/yolo11s_tci.pt"
MODEL_PATH = Path(__file__).parent / "yolo11s_tci.pt"
EXPECTED_SHA256 = "81E5B661B880CEFA304A149FB7AE603FA4ECA7DF7226BEF54952D30862ED910B"


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        # Read in chunks for large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def verify_checksum(file_path: Path) -> bool:
    """Verify file checksum matches expected hash."""
    if not EXPECTED_SHA256 or EXPECTED_SHA256 == "":
        print("Warning: No checksum configured, skipping verification")
        return True

    print(f"Verifying checksum...")
    actual_hash = calculate_sha256(file_path)

    if actual_hash == EXPECTED_SHA256:
        print(f"Checksum verified: {actual_hash[:16]}...")
        return True
    else:
        print(f"Checksum mismatch!")
        print(f"Expected: {EXPECTED_SHA256}")
        print(f"Got:      {actual_hash}")
        return False


def download_model(force: bool = False) -> Path:
    """
    Download YOLO11s marine vessel model from HuggingFace.

    Args:
        force: Force re-download even if file exists

    Returns:
        Path to downloaded model

    Raises:
        RuntimeError: If download fails or checksum mismatch
    """
    # Check if model already exists
    if MODEL_PATH.exists() and not force:
        print(f"Model already exists: {MODEL_PATH}")

        # Verify existing file
        if verify_checksum(MODEL_PATH):
            return MODEL_PATH
        else:
            print("Existing model failed checksum, re-downloading...")
            MODEL_PATH.unlink()

    # Create models directory
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Download model
    print(f"Downloading YOLO11s model from HuggingFace...")
    print(f"URL: {MODEL_URL}")
    print(f"Size: ~19 MB")

    try:
        def report_progress(block_num, block_size, total_size):
            """Show download progress."""
            downloaded = block_num * block_size
            percent = min(100, downloaded * 100 / total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\rProgress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="")

        urlretrieve(MODEL_URL, MODEL_PATH, reporthook=report_progress)
        print()  # New line after progress

    except URLError as e:
        raise RuntimeError(f"Failed to download model: {e}")

    # Verify downloaded file
    if not verify_checksum(MODEL_PATH):
        MODEL_PATH.unlink()
        raise RuntimeError("Downloaded model failed checksum verification")

    print(f"Model downloaded successfully: {MODEL_PATH}")
    print(f"Size: {MODEL_PATH.stat().st_size / (1024*1024):.2f} MB")

    return MODEL_PATH


if __name__ == "__main__":
    """Command-line usage: python models/download_model.py [--force]"""
    force = "--force" in sys.argv

    try:
        model_path = download_model(force=force)
        print(f"\nModel ready: {model_path}")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
