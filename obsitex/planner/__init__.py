import logging
import re
from pathlib import Path
from typing import Optional, Sequence, Set, Tuple

import yaml

from obsitex.planner.jobs import AddBibliography, AddHeader, AddText, PlannedJob
from obsitex.planner.links import find_all_citations, find_all_links
from obsitex.utils import assure_dir, assure_file, read_file


def parse_yaml_properties(text: str) -> Tuple[str, dict]:
    properties = {}

    if text.startswith("---"):
        # Find the end of the properties
        end_properties = text.find("---", 3)

        # Remove the properties from the file contents
        yaml_configs = text[3:end_properties]

        # Try to load the properties, if it doesn't work, ignore
        properties = yaml.safe_load(yaml_configs)

        # Clean the props from the text
        text = text[end_properties + 3 :].strip()

    return text, properties


class ExecutionPlan:
    def __init__(
        self,
        graphics_path: Optional[Path] = None,
        bibtex_database_path: Optional[Path] = None,
        implictly_add_bibtex: bool = True,
    ):
        self.graphics_path = graphics_path
        self.bibtex_database_path = bibtex_database_path
        self.implictly_add_bibtex = implictly_add_bibtex

        # Check that if the paths are provided, they are valid
        assure_dir(self.graphics_path)
        assure_file(self.bibtex_database_path)

        # Variables to store extracted data
        self._citation_keys: Set[str] = set()
        self._n_files_read = 0

        # Used to specify the jobs that will run in the execution plan
        self._jobs: Sequence[PlannedJob] = []

    @property
    def n_files_read(self) -> int:
        return self._n_files_read

    @property
    def num_headers(self) -> int:
        return len([job for job in self._jobs if isinstance(job, AddHeader)])

    def iter_jobs(self):
        # Find the first job in the appendix
        appendix_job_idx = None

        for idx, job in enumerate(self._jobs):
            if job.is_in_appendix:
                appendix_job_idx = idx
                break

        if appendix_job_idx is None:
            appendix_job_idx = len(self._jobs)

        # Iter through the non appendix job, add bibliography job and then the appendix jobs
        for job in self._jobs[:appendix_job_idx]:
            yield job

        # When this is called, it's assumed that all files have been added
        # to the execution plan. Thus we need to check if we should add the bibliography
        # here or not. - should always be the last job
        if self.implictly_add_bibtex and len(self._citation_keys) > 0:
            if (
                self.bibtex_database_path is None
                or not self.bibtex_database_path.is_file()
            ):
                raise FileNotFoundError(
                    f"BibTeX database not found at {self.bibtex_database_path}, please provide a valid path if you're using citations."
                )

            add_bib_job = AddBibliography(
                self._citation_keys, self.bibtex_database_path
            )
            yield add_bib_job

        for job in self._jobs[appendix_job_idx:]:
            job.mark_as_appendix()
            yield job

    def add_citations(self, text: str):
        self._citation_keys.update(find_all_citations(text))

    def add_file(self, file_path: Path):
        assure_file(file_path)

        # Read the file contents
        file_contents = read_file(file_path)
        self._n_files_read += 1

        # Extract citations from the file
        self.add_citations(file_contents)

        # If exist, parse the YAML properties
        try:
            file_contents, properties = parse_yaml_properties(file_contents)
        except:
            logging.error(
                f"Error parsing YAML properties from {file_path}, ignoring..."
            )
            properties = {}

        # Single files have no deps
        add_text_job = AddText(file_contents)
        add_text_job.update_configs(properties)

        self._jobs.append(add_text_job)

    def add_dir(
        self,
        dir_path: Path,
        index_file: Optional[str] = None,
        max_depth: int = 10,
        base_hlevel: int = -2,
    ):
        assure_dir(dir_path)

        if index_file is None:
            index_file = "Index"

        # Perform depth-first search to find all files
        # Base hlevel is -1 because index doesn't produce headers
        stack = [(dir_path, index_file, base_hlevel - 1, 0)]
        global_configs, is_index = {}, True

        while len(stack) > 0:
            current_base_path, current_file, current_hlevel, current_depth = stack.pop()

            if current_depth < max_depth:
                file_contents = read_file(current_base_path / f"{current_file}.md")
                self._n_files_read += 1

                # Each file can have properties configured in YAML
                properties = {}

                # Find all links are remove them from the text
                clean_text, links = find_all_links(file_contents)

                if clean_text != "":
                    try:
                        clean_text, properties = parse_yaml_properties(clean_text)
                    except:
                        logging.error(
                            f"Error parsing YAML properties from {current_file}.md, ignoring..."
                        )
                        properties = {}

                    if is_index:
                        global_configs.update(properties)

                if not is_index:
                    properties.update(global_configs)

                # If not the index file, add a header
                if current_hlevel >= base_hlevel:
                    add_header_job = AddHeader(current_file, current_hlevel)
                    add_header_job.update_configs(properties)

                    self._jobs.append(add_header_job)

                if clean_text != "":
                    add_text_job = AddText(clean_text)
                    add_text_job.update_configs(properties)

                    self._jobs.append(add_text_job)
                    self.add_citations(clean_text)

                for link in reversed(links):
                    # Might be pointing to a file in the same folder
                    # or a subdirectory
                    new_base_path = current_base_path / link

                    if not new_base_path.is_dir():
                        new_base_path = current_base_path

                        if not (new_base_path / f"{link}.md").is_file():
                            raise ValueError(
                                f"File {link} not found in {new_base_path}"
                            )

                    stack.append(
                        (new_base_path, link, current_hlevel + 1, current_depth + 1)
                    )
            else:
                raise ValueError(
                    f"Max depth of {max_depth} reached, please check for cycles in your links."
                )

            if is_index:
                is_index = False

        logging.info(f"Added {len(self._jobs)} jobs to the execution plan.")

    def show(self, text_limit: int = 50, show_configs: bool = False):
        for order, job in enumerate(self._jobs, start=1):
            if isinstance(job, AddText):
                if text_limit >= 0:
                    text_content = job.text[:text_limit]
                logging.info(f"{order}. Adding text: {text_content}...")
            elif isinstance(job, AddHeader):
                logging.info(
                    f"{order}. Adding header: {job.header} with level {job.level}..."
                )
            else:
                logging.warning(f"{order}. Unknown job type: {job}")

        logging.info(f"Printing table of contents...")

        if self.num_headers == 0:
            hlevel_zero_adjusted = 0
        else:
            hlevel_zero_adjusted = min(
                [job.level for job in self._jobs if isinstance(job, AddHeader)]
            )

            if hlevel_zero_adjusted < 0:
                hlevel_zero_adjusted = -hlevel_zero_adjusted

            # Used for add text jobs to know the header level above
            prev_header_level = 0
            header_regex = r"(#+)\s*(.+)\s*\n"
            tob_content = []

            for job in self._jobs:
                if isinstance(job, AddHeader):
                    level = job.level + hlevel_zero_adjusted + 1
                    title = job.header
                    prev_header_level = level
                    tob_content.append((level, title, job.configs))
                elif isinstance(job, AddText):
                    level = prev_header_level

                    # Find all the headers contains inside
                    headers_in_text = re.findall(header_regex, job.text)

                    for header_level, header_title in headers_in_text:
                        level = len(header_level) + prev_header_level
                        tob_content.append((level, header_title, None))

            for level, header, configs in tob_content:
                if configs is not None and show_configs:
                    logging.info(f"{' '*(level-1)}| {header} {configs}")
                else:
                    logging.info(f"{' '*(level-1)}| {header}")
