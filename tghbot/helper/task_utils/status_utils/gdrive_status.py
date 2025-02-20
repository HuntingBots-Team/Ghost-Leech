from tghbot.helper.ext_utils.status_utils import (
    MirrorStatus,
    get_readable_file_size,
    get_readable_time,
)
from pkg_resources import get_distribution


class GoogleDriveStatus:
    def __init__(
            self,
            listener,
            obj,
            gid,
            status
        ):
        self.listener = listener
        self._obj = obj
        self._size = self.listener.size
        self._gid = gid
        self._status = status
        self.engine = f"G-Api v{self._eng_ver()}"

    def _eng_ver(self):
        return get_distribution("google-api-python-client").version

    def processed_bytes(self):
        return get_readable_file_size(self._obj.processed_bytes)

    def size(self):
        return get_readable_file_size(self._size)

    def status(self):
        if self._status == "up":
            return MirrorStatus.STATUS_UPLOADING
        elif self._status == "dl":
            return MirrorStatus.STATUS_DOWNLOADING
        else:
            return MirrorStatus.STATUS_CLONING

    def name(self):
        return self.listener.name

    def gid(self) -> str:
        return self._gid

    def progress_raw(self):
        try:
            return self._obj.processed_bytes / self._size * 100
        except:
            return 0

    def progress(self):
        return f"{round(self.progress_raw(), 2)}%"

    def speed(self):
        return f"{get_readable_file_size(self._obj.speed)}/s"

    def eta(self):
        try:
            seconds = (self._size - self._obj.processed_bytes) / self._obj.speed
            return get_readable_time(seconds)
        except:
            return "-"

    def task(self):
        return self._obj
