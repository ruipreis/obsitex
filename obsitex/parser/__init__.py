import logging
from pathlib import Path
from typing import Optional, Sequence

import bibtexparser
from jinja2 import Environment

from obsitex.constants import (
    DEFAULT_APPENDIX_MARKER,
    DEFAULT_BIBLIOGRAPHY_MARKER,
    DEFAULT_HLEVEL_MAPPING,
    DEFAULT_JINJA2_JOB_TEMPLATE,
    DEFAULT_JINJA2_MAIN_TEMPLATE,
)
from obsitex.parser.blocks import (
    PARSEABLE_BLOCKS,
    LaTeXBlock,
    MarkerBlock,
    Paragraph,
    Section,
)
from obsitex.planner import ExecutionPlan
from obsitex.planner.jobs import AddBibliography, AddHeader, AddText, PlannedJob


class ObsidianParser:
    def __init__(
        self,
        bibtex_database_path: Optional[Path] = None,
        implictly_add_bibtex: bool = True,
        out_bitex_path: Optional[Path] = None,
        graphics_folder: Optional[Path] = None,
        job_template: str = DEFAULT_JINJA2_JOB_TEMPLATE,
        main_template: str = DEFAULT_JINJA2_MAIN_TEMPLATE,
        hlevel_mapping: dict = DEFAULT_HLEVEL_MAPPING,
        appendix_marker: str = DEFAULT_APPENDIX_MARKER,
        bibliography_marker: str = DEFAULT_BIBLIOGRAPHY_MARKER,
        base_hlevel: int = 0,
    ):
        self.job_template = job_template
        self.main_template = main_template
        self.hlevel_mapping = hlevel_mapping
        self.appendix_marker = appendix_marker
        self.bibliography_marker = bibliography_marker
        self.out_bitex_path = out_bitex_path

        # Construct an execution plan, which will collect the jobs to run from
        # the files and pths provided
        self.execution_plan = ExecutionPlan(
            bibtex_database_path=bibtex_database_path,
            implictly_add_bibtex=implictly_add_bibtex,
        )

        # Extra arguments that should be injected when converting to latex
        self.extra_args = {
            "hlevel_mapping": self.hlevel_mapping,
            "graphics_folder": graphics_folder,
        }

        # Flag to continuously check if in appendix
        self.in_appendix = False

        # Set of blocks that will be added to the main tex file
        self.blocks: Sequence[LaTeXBlock] = []

        # Keep track of the latest header level
        self.base_hlevel = base_hlevel
        self.latest_parsed_hlevel = base_hlevel

    def add_file(self, file_path: Path, adjust_hlevel: bool = True):
        # By default adding a file assumes a single file structure
        if adjust_hlevel:
            self.latest_parsed_hlevel = self.base_hlevel - 1

        self.execution_plan.add_file(file_path)

    def add_dir(self, dir_path: Path):
        self.execution_plan.add_dir(dir_path)

    def apply_jobs(self):
        for job in self.execution_plan.iter_jobs():
            self.parse_job(job)

    def to_latex(self) -> str:
        # Create template for job level and main
        job_template = Environment().from_string(self.job_template)
        main_template = Environment().from_string(self.main_template)

        # Render each block onto the job template
        rendered_blocks = "\n\n".join(
            [
                job_template.render(
                    parsed_latex_content=block.formatted_text(**self.extra_args),
                    **block.metadata,
                )
                for block in self.blocks
            ]
        )

        # Render the main template with the rendered blocks
        # the global variables are shared by all blocks, we use the first
        # block for simplicity
        if len(self.blocks) > 0:
            global_configs = self.blocks[0].metadata
        else:
            global_configs = {}

        return main_template.render(
            parsed_latex_content=rendered_blocks,
            **global_configs,
        )

    def parse_job(self, job: PlannedJob) -> str:
        if not self.in_appendix:
            self.in_appendix = job.is_in_appendix

            # If in appendix, add the appendix marker
            if self.in_appendix:
                marker_block = MarkerBlock(self.appendix_marker)
                marker_block.metadata = job.configs
                self.blocks.append(marker_block)
                logging.info("Added appendix marker to the parser.")

        # Given a job, returns the corresponding latex code
        if isinstance(job, AddHeader):
            self.latest_parsed_hlevel = job.level
            return self._parse_header(job)
        elif isinstance(job, AddText):
            return self._parse_text(job)
        elif isinstance(job, AddBibliography):
            return self._parse_bibliography(job)
        else:
            raise ValueError(f"Unknown job type {job}")

    def _parse_header(self, job: AddHeader):
        section_block = Section(job.level, job.header)
        self.blocks.append(section_block)
        logging.info(
            f'Added header "{job.header}" with level {job.level} to the parser.'
        )

    def _parse_text(self, job: AddText):
        lines = job.text.split("\n")
        curr_i = 0
        initial_block_count = len(self.blocks)

        while curr_i < len(lines):
            found_block = False

            for block_class in PARSEABLE_BLOCKS:
                block_instance = block_class.detect_block(lines, curr_i)

                if block_instance is not None:
                    block, curr_i = block_instance

                    if isinstance(block, Section):
                        block.hlevel += self.latest_parsed_hlevel

                    found_block = True
                    block.metadata = job.configs
                    self.blocks.append(block)
                    break

            if not found_block:
                # If remaining, assume it's a paragraph
                paragraph_block = Paragraph(lines[curr_i])
                paragraph_block.metadata = job.configs
                self.blocks.append(paragraph_block)

            curr_i += 1

        logging.info(
            f"Added {len(self.blocks) - initial_block_count} blocks to the parser, total {len(self.blocks)}."
        )

    def _parse_bibliography(self, job: AddBibliography):
        if self.out_bitex_path is None:
            raise ValueError("Bibliography was added but no output path was set.")

        # Select the keys to be included in the bibliography, and export
        with open(job.bibtex_path, "r") as file:
            bib_database = bibtexparser.load(file)

        # Index the bib tex keys and verify if all are present
        bib_keys = {entry["ID"]: entry for entry in bib_database.entries}
        missing_keys = [key for key in job.citations if key not in bib_keys]

        if len(missing_keys) > 0:
            raise ValueError(
                f"Missing {len(missing_keys)} keys in bibliography: {missing_keys}"
            )

        # Write the selected entries to a new BibTeX file
        new_db = bibtexparser.bparser.BibTexParser()  # Get a new BibDatabase instance
        new_db.entries = [bib_keys[key] for key in job.citations]

        with open(self.out_bitex_path, "w") as file:
            bibtexparser.dump(new_db, file)

        # Add the proper marker
        marker_block = MarkerBlock(self.bibliography_marker)
        marker_block.metadata = job.configs
        self.blocks.append(marker_block)
        logging.info("Added bibliography marker to the parser.")
