"""Configuration management for Pontos ship detection system."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class PontosConfig:
    """Main configuration for Pontos."""

    # Paths
    model_path: Path = Path("models/yolo11s_tci.pt")
    data_dir: Path = Path("data")
    output_dir: Path = Path("runs")

    # Sentinel Hub API
    sentinel_client_id: Optional[str] = os.getenv("SH_CLIENT_ID")
    sentinel_client_secret: Optional[str] = os.getenv("SH_CLIENT_SECRET")

    # Detection parameters
    confidence_threshold: float = 0.05
    patch_size: int = 320
    patch_overlap: float = 0.5
    device: str = "0"  # GPU device ID

    # Processing
    max_workers: int = 4
    batch_size: int = 8

    @classmethod
    def from_env(cls) -> "PontosConfig":
        """Load configuration from environment variables."""
        return cls(
            sentinel_client_id=os.getenv("SH_CLIENT_ID"),
            sentinel_client_secret=os.getenv("SH_CLIENT_SECRET"),
        )

    def validate(self) -> None:
        """Validate configuration."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        if not self.sentinel_client_id or not self.sentinel_client_secret:
            raise ValueError("Sentinel Hub credentials not configured")


# Global config instance
config = PontosConfig.from_env()
