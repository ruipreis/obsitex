from abc import ABC
from pathlib import Path
from typing import Set


class PlannedJob(ABC):
    def __init__(self):
        self.configs = {}

    def update_configs(self, kwargs: dict):
        self.configs.update(kwargs)

    @property
    def is_in_appendix(self) -> bool:
        return self.configs.get("appendix", False)

    def mark_as_appendix(self):
        self.configs["appendix"] = True


class AddText(PlannedJob):
    def __init__(self, text: str):
        super().__init__()
        self.text = text


class AddHeader(PlannedJob):
    def __init__(self, header: str, level: int):
        super().__init__()
        self.header = header
        self.level = level


class AddBibliography(PlannedJob):
    def __init__(self, citations: Set[str], bibtex_path: Path):
        super().__init__()
        self.citations = citations
        self.bibtex_path = bibtex_path
