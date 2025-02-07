from typing import Optional
from pathlib import Path


def assure_dir(path: Optional[Path]):
    if path is not None and not path.is_dir():
        raise ValueError(f"Path {path} is not a directory.")


def assure_file(path: Optional[Path]):
    if path is not None and not path.is_file():
        raise ValueError(f"Path {path} is not a file.")


def read_file(file_path: Path) -> str:
    assure_file(file_path)

    with open(file_path, "r") as file:
        return file.read()
