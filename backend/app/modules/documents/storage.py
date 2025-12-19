from webdav3.client import Client
from app.core.settings.config import settings
from tempfile import NamedTemporaryFile
import os


class NextcloudStorage:
    def __init__(self):
        self.client = Client({
            "webdav_hostname": settings.NEXTCLOUD_URL,
            "webdav_login": settings.NEXTCLOUD_USER,
            "webdav_password": settings.NEXTCLOUD_PASSWORD,
        })

    def _sanitize(self, path: str) -> str:
        return path.strip().lstrip("/")

    def _ensure_dirs(self, remote_path: str) -> None:
        remote_path = self._sanitize(remote_path)
        parts = remote_path.split("/")[:-1]
        current = ""

        for part in parts:
            current = f"{current}/{part}" if current else part
            try:
                self.client.mkdir(current)
            except Exception:
                pass

    def upload(self, remote_path: str, content: bytes) -> None:
        remote_path = self._sanitize(remote_path)

        self._ensure_dirs(remote_path)

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
        with NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            self.client.download(
                remote_path=remote_path,
                local_path=tmp_path,
            )

            with open(tmp_path, "rb") as f:
                return f.read()
        finally:
            os.remove(tmp_path)

    def delete(self, remote_path: str) -> None:
        self.client.clean(remote_path)

    def exists(self, remote_path: str) -> bool:
        return self.client.check(remote_path)
