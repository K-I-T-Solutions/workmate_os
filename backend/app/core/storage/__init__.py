"""
Storage abstraction layer for WorkmateOS

Supports multiple backends:
- Local filesystem
- Nextcloud WebDAV
- S3 (future)
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
class StorageBackend(Protocol):
    """
    Storage backend protocol/interface.

    All storage backends must implement these methods.
    """

    def upload(self, remote_path: str, content: bytes) -> None:
        """
        Upload content to storage.

        Args:
            remote_path: Path in storage (e.g., 'invoices/RE-2025-0001.pdf')
            content: File content as bytes
        """
        ...

    def download(self, remote_path: str) -> bytes:
        """
        Download content from storage.

        Args:
            remote_path: Path in storage

        Returns:
            File content as bytes
        """
        ...

    def delete(self, remote_path: str) -> None:
        """
        Delete file from storage.

        Args:
            remote_path: Path in storage
        """
        ...

    def exists(self, remote_path: str) -> bool:
        """
        Check if file exists in storage.

        Args:
            remote_path: Path in storage

        Returns:
            True if file exists, False otherwise
        """
        ...

    def get_full_path(self, remote_path: str) -> str:
        """
        Get full path/URL for file.

        For local storage: absolute filesystem path
        For cloud storage: remote path or download URL

        Args:
            remote_path: Relative path in storage

        Returns:
            Full path or URL
        """
        ...


__all__ = ["StorageBackend"]
