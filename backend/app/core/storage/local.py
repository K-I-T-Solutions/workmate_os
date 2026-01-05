"""
Local filesystem storage backend
"""
import os
from pathlib import Path
from typing import Optional


class LocalStorage:
    """
    Local filesystem storage implementation.

    Stores files in a local directory.
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize local storage.

        Args:
            base_path: Base directory for storage (e.g., '/app/uploads')
                      If None, uses '/tmp/workmate_storage'
        """
        self.base_path = Path(base_path) if base_path else Path("/tmp/workmate_storage")
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, remote_path: str) -> Path:
        """Get full filesystem path."""
        # Remove leading slash and sanitize
        clean_path = remote_path.lstrip("/")
        return self.base_path / clean_path

    def upload(self, remote_path: str, content: bytes) -> None:
        """Upload file to local filesystem."""
        full_path = self._get_full_path(remote_path)

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(full_path, "wb") as f:
            f.write(content)

    def download(self, remote_path: str) -> bytes:
        """Download file from local filesystem."""
        full_path = self._get_full_path(remote_path)

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {remote_path}")

        with open(full_path, "rb") as f:
            return f.read()

    def delete(self, remote_path: str) -> None:
        """Delete file from local filesystem."""
        full_path = self._get_full_path(remote_path)

        if full_path.exists():
            full_path.unlink()

    def exists(self, remote_path: str) -> bool:
        """Check if file exists in local filesystem."""
        full_path = self._get_full_path(remote_path)
        return full_path.exists()

    def get_full_path(self, remote_path: str) -> str:
        """Get absolute filesystem path."""
        return str(self._get_full_path(remote_path))
