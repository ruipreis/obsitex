import logging
from pathlib import Path
from typing import Optional, Sequence

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
from obsitex.planner.jobs import AddBibliography, AddHeader, AddText, PlannedJob


class MarkdownJobParser:
    def __init__(
        self,
        graphics_folder: Optional[Path] = None,
        job_template: str = DEFAULT_JINJA2_JOB_TEMPLATE,
        main_template: str = DEFAULT_JINJA2_MAIN_TEMPLATE,
        hlevel_mapping: dict = DEFAULT_HLEVEL_MAPPING,
        appendix_marker: str = DEFAULT_APPENDIX_MARKER,
        bibliography_marker: str = DEFAULT_BIBLIOGRAPHY_MARKER,
    ):
        self.job_template = job_template
        self.main_template = main_template
        self.hlevel_mapping = hlevel_mapping
        self.appendix_marker = appendix_marker
        self.bibliography_marker = bibliography_marker

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
        self.latest_parsed_hlevel = 0

    def to_latex(self) -> str:
        return "\n\n".join(
            [block.formatted_text(**self.extra_args) for block in self.blocks]
        )

    def parse_job(self, job: PlannedJob) -> str:
        if not self.in_appendix:
            self.in_appendix = job.is_in_appendix

            # If in appendix, add the appendix marker
            if self.in_appendix:
                self.blocks.append(MarkerBlock(self.appendix_marker))
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
                    self.blocks.append(block)
                    break

            if not found_block:
                # If remaining, assume it's a paragraph
                self.blocks.append(Paragraph(lines[curr_i]))

            curr_i += 1

        logging.info(
            f"Added {len(self.blocks) - initial_block_count} blocks to the parser, total {len(self.blocks)}."
        )

    def _parse_bibliography(self, job: AddBibliography):
        self.blocks.append(MarkerBlock(self.bibliography_marker))
        logging.info("Added bibliography marker to the parser.")
