import logging
import os
import pathlib
from http.server import HTTPServer, SimpleHTTPRequestHandler
from shutil import copyfile
from threading import Thread
from typing import Any, Optional

from .client import StorageClient, StorageClientException

logger = logging.getLogger(__name__)


class LocalStorageClient(StorageClient):
    ip = "0.0.0.0"
    port = 8001

    def __init__(self, workspace: str) -> None:
        self.workspace = workspace

    def save(self, key: str, file: Any) -> None:
        full_path = os.path.join(self.workspace, key)
        pathlib.Path(full_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(full_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        except StorageClientException as e:
            raise StorageClientException(e)

    def get_url(self, key: str, *, content_type: Optional[str] = None) -> str:
        return f"http://{self.ip}:{self.port}/{key}"

    def get_attachment_url(
        self, key: str, *, content_type: Optional[str] = None, filename: Optional[str] = None
    ) -> str:
        return self.get_url(key=key, content_type=content_type)

    def copy(self, src: str) -> None:
        dest_path = os.path.join(self.workspace, src)
        pathlib.Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
        copyfile(src, dest_path)


class LocalStorageHttpServerThread(Thread):
    def __init__(self, ip: str, port: int, directory: str) -> None:
        Thread.__init__(self)
        self._ip = ip
        self._port = port
        self._directory = directory

    def run(self) -> None:
        class LocalStorageHTTPRequestHandler(SimpleHTTPRequestHandler):
            def __init__(self_, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, directory=self._directory, **kwargs)  # type: ignore

        logger.debug(f"running local storage http server @ {self._ip}:{self._port}")
        HTTPServer((self._ip, self._port), LocalStorageHTTPRequestHandler).serve_forever()


class LocalStorageClientWithServer(LocalStorageClient):
    def __init__(self, workspace: str, run_server: bool = True) -> None:
        super().__init__(workspace)
        if run_server:
            LocalStorageHttpServerThread(self.ip, self.port, self.workspace).start()
