"""
Storage factory - creates storage backend based on configuration
"""
from typing import Literal
from app.core.settings.config import settings
from app.core.storage import StorageBackend
from app.core.storage.local import LocalStorage
from app.core.storage.nextcloud import NextcloudStorage


StorageType = Literal["local", "nextcloud", "s3"]


def get_storage_backend(backend_type: str | None = None) -> StorageBackend:
    """
    Get storage backend instance based on configuration.

    Args:
        backend_type: Storage backend type ('local', 'nextcloud', 's3')
                     If None, uses settings.STORAGE_BACKEND

    Returns:
        Storage backend instance

    Raises:
        ValueError: If backend type is unknown
    """
    backend = backend_type or getattr(settings, "STORAGE_BACKEND", "local")

    if backend == "local":
        base_path = getattr(settings, "UPLOAD_DIR", "/app/uploads")
        return LocalStorage(base_path=base_path)

    elif backend == "nextcloud":
        return NextcloudStorage()

    elif backend == "s3":
        # TODO: Implement S3 backend
        raise NotImplementedError("S3 storage backend not yet implemented")

    else:
        raise ValueError(f"Unknown storage backend: {backend}")


# Global storage instance (singleton)
_storage_instance: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """
    Get global storage instance (singleton).

    This is the recommended way to get a storage backend.
    The instance is created once and reused.

    Returns:
        Storage backend instance
    """
    global _storage_instance

    if _storage_instance is None:
        _storage_instance = get_storage_backend()

    return _storage_instance


def reset_storage() -> None:
    """
    Reset global storage instance.

    Useful for testing or when changing storage backend at runtime.
    """
    global _storage_instance
    _storage_instance = None
