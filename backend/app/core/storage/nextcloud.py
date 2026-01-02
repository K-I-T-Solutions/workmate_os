"""
Nextcloud WebDAV storage backend
"""
from webdav3.client import Client
from app.core.settings.config import settings
from tempfile import NamedTemporaryFile
import os
import requests
from requests.auth import HTTPBasicAuth


class NextcloudStorage:
    """
    Nextcloud WebDAV storage implementation.

    Stores files in Nextcloud using WebDAV protocol.
    """

    def __init__(self):
        """Initialize Nextcloud WebDAV client."""
        self.client = Client({
            "webdav_hostname": settings.NEXTCLOUD_URL,
            "webdav_login": settings.NEXTCLOUD_USER,
            "webdav_password": settings.NEXTCLOUD_PASSWORD,
        })
        self.base_path = settings.NEXTCLOUD_BASE_PATH

    def _sanitize(self, path: str) -> str:
        """Remove leading/trailing slashes and clean path."""
        clean = path.strip().lstrip("/")
        if self.base_path:
            return f"{self.base_path.strip('/')}/{clean}"
        return clean

    def _ensure_dirs(self, remote_path: str) -> None:
        """Create parent directories if they don't exist."""
        remote_path = self._sanitize(remote_path)
        parts = remote_path.split("/")[:-1]
        current = ""

        for part in parts:
            current = f"{current}/{part}" if current else part
            try:
                self.client.mkdir(current)
            except Exception:
                # Directory already exists or can't be created
                pass

    def upload(self, remote_path: str, content: bytes) -> None:
        """
        Upload file to Nextcloud.

        Args:
            remote_path: Path in Nextcloud (e.g., 'workmate/invoices/RE-2025-0001.pdf')
            content: File content as bytes
        """
        remote_path = self._sanitize(remote_path)
        self._ensure_dirs(remote_path)

        # Write to temporary file
        with NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            self.client.upload(
                remote_path=remote_path,
                local_path=tmp_path,
            )
        finally:
            os.remove(tmp_path)

    def download(self, remote_path: str) -> bytes:
        """
        Download file from Nextcloud using direct HTTP GET.

        Args:
            remote_path: Path in Nextcloud

        Returns:
            File content as bytes
        """
        remote_path = self._sanitize(remote_path)

        # Build full URL
        url = f"{settings.NEXTCLOUD_URL}/{remote_path}"

        # Download using requests with basic auth
        response = requests.get(
            url,
            auth=HTTPBasicAuth(settings.NEXTCLOUD_USER, settings.NEXTCLOUD_PASSWORD),
            timeout=30
        )

        if response.status_code == 404:
            raise FileNotFoundError(f"File not found: {remote_path}")

        response.raise_for_status()
        return response.content

    def delete(self, remote_path: str) -> None:
        """
        Delete file from Nextcloud.

        Args:
            remote_path: Path in Nextcloud
        """
        remote_path = self._sanitize(remote_path)
        self.client.clean(remote_path)

    def exists(self, remote_path: str) -> bool:
        """
        Check if file exists in Nextcloud.

        Args:
            remote_path: Path in Nextcloud

        Returns:
            True if file exists, False otherwise
        """
        remote_path = self._sanitize(remote_path)
        return self.client.check(remote_path)

    def get_full_path(self, remote_path: str) -> str:
        """
        Get full path in Nextcloud.

        Args:
            remote_path: Relative path

        Returns:
            Full Nextcloud path
        """
        return self._sanitize(remote_path)
