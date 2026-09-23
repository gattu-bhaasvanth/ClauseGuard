import os
import hashlib
import shutil
from pathlib import Path
from typing import Tuple
from app.config import settings


class StorageManager:
    """Manages file storage, paths, and checksums in data/uploads/."""

    def __init__(self, upload_dir: str = None):
        if upload_dir:
            self.upload_dir = Path(upload_dir)
        else:
            root_dir = Path(__file__).resolve().parent.parent.parent.parent
            self.upload_dir = root_dir / "data" / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_upload_stream(
        self, file_content: bytes, original_filename: str
    ) -> Tuple[Path, str, str]:
        """
        Saves bytes to disk, returning (saved_path, sha256_hash, formatted_size).
        """
        sha256 = hashlib.sha256(file_content).hexdigest()
        sanitized_name = Path(original_filename).name.replace(" ", "_")
        stored_filename = f"{sha256[:10]}_{sanitized_name}"
        target_path = self.upload_dir / stored_filename

        with open(target_path, "wb") as f:
            f.write(file_content)

        size_bytes = len(file_content)
        size_formatted = self.format_file_size(size_bytes)
        return target_path, sha256, size_formatted

    @staticmethod
    def format_file_size(bytes_count: int) -> str:
        if bytes_count == 0:
            return "0 KB"
        k = 1024
        sizes = ["Bytes", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(bytes_count) / math.log(k)))
        if i >= len(sizes):
            i = len(sizes) - 1
        p = math.pow(k, i)
        s = round(bytes_count / p, 1)
        return f"{s} {sizes[i]}"


storage_manager = StorageManager()
