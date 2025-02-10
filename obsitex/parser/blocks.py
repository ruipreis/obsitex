import re
from abc import ABC, abstractmethod
from io import StringIO
from pathlib import Path
from typing import Optional, Sequence, Tuple, Type

import yaml

from obsitex.constants import CALLOUT_CONFIG_MARKER, QUOTE_MARKER, SPECIAL_CALLOUTS
from obsitex.parser.formatting import detect_command, find_next_index, format_text


class LaTeXBlock(ABC):
    def __init__(self, content, in_latex=False):
        self.content = content
        self.parent = None  # Only Section and Project objects can be parents
        self.in_latex = in_latex
        self._is_after_appendix = False
        self.metadata = {}

    @property
    def is_after_appendix(self):
        return self._is_after_appendix

    @is_after_appendix.setter
    def is_after_appendix(self, value):
        self._is_after_appendix = value

    def formatted_text(self, **kwargs):
        if self.in_latex:
            if isinstance(self.content, str):
                return self.content
            else:
                return "\n".join(self.content)
        else:
            if isinstance(self.content, str):
                text_lines = format_text([self.content])
            else:
                text_lines = format_text(self.content)

        return "\n".join(text_lines)

    @staticmethod
    @abstractmethod
    def detect_block(
        lines: Sequence[str], index: int
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        """
        Detects if the block is present in the lines starting from the index.

        Returns the index of the last line of the block if the block is detected.
        """
        pass


class Paragraph(LaTeXBlock):
    def __init__(self, content):
        super().__init__(content, in_latex=False)

    @staticmethod
    def detect_block(lines, index):
        return None


class MarkerBlock(LaTeXBlock):
    def __init__(self, content):
        super().__init__(content, in_latex=True)

    # Used to inject latex code for flow control, e.g.: appendix, bibliography
    @staticmethod
    def detect_block(lines, index):
        return None


class Section(LaTeXBlock):
    def __init__(self, hlevel: int, title: str):
        super().__init__(None)
        self.hlevel = hlevel
        self.title = title

    @property
    def label(self):
        reformatted_title = re.sub(r"\W", "_", self.title)
        return f"sec:{reformatted_title}"

    def __repr__(self):
        return f'Section(hlevel={self.hlevel}, title="{self.title}")'

    def formatted_text(self, **kwargs):
        if "hlevel_mapping" not in kwargs:
            raise ValueError("hlevel_mapping not provided in kwargs")
        else:
            hlevel_mapping = kwargs["hlevel_mapping"]

        if self.hlevel not in hlevel_mapping:
            raise ValueError(f"Header level {self.hlevel} not found in hlevel_mapping")

        content = (
            f"\\{hlevel_mapping[self.hlevel]}{{{self.title}}}\\label{{{self.label}}}"
        )

        return content

    @staticmethod
    def detect_block(
        lines: Sequence[str], index: int
    ) -> Optional[Tuple["Section", int]]:
        header_match = re.match(r"^(#+)\s*(.+)\s*", lines[index])

        if header_match is not None:
            hlevel = len(header_match.group(1))
            title = header_match.group(2)

            return Section(hlevel, title), index

        return None


class Equation(LaTeXBlock):
    def __init__(self, content, label: Optional[str] = None):
        super().__init__(content)
        self.label = label

    def formatted_text(self, **kwargs):
        equation_text = "\\begin{equation}\n"

        if self.label is not None:
            equation_text += f"\t\\label{{{self.label}}}\n"

        equation_text += f"\t{self.content}\n\\end{{equation}}\n"

        return equation_text

    def __repr__(self):
        return f"Equation(content={self.content}, label={self.label})"

    @staticmethod
    def detect_block(
        lines: Sequence[str], index: int
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        def _is_equation(line):
            return line.startswith("$$")

        if _is_equation(lines[index]):
            # Get the label if it exists
            label = detect_command(lines[index])

            # Find the end of the equation
            end_index = find_next_index(lines, _is_equation, index + 1)

            # Extract the equation content
            equation_content = "\n".join(lines[index + 1 : end_index])

            return Equation(equation_content, label), end_index

        return None


class AbstractList(LaTeXBlock):
    def __init__(self, lines: Sequence[str]):
        super().__init__(lines)
        self.lines = lines

    @abstractmethod
    def list_type(self):
        pass

    def formatted_text(self, **kwargs):
        list_type = self.list_type()
        content = f"\\begin{{{list_type}}}\n"

        for line in format_text(self.lines):
            content += f"\t\\item {line}\n"

        content += f"\\end{{{list_type}}}\n"

        return content

    def __repr__(self):
        return f"{self.list_type()} list (lines={self.lines})"

    @staticmethod
    def detect_block(
        lines: Sequence[str],
        index: int,
        item_regex_pattern: str,
        instance_class: Type["LaTeXBlock"],
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        regex_pattern = item_regex_pattern

        def _is_list_item(line):
            return re.match(regex_pattern, line)

        not_is_list_item = lambda line: not _is_list_item(line)

        if _is_list_item(lines[index]):
            # Find the end of the list
            end_index = find_next_index(lines, not_is_list_item, index + 1)

            # Extract the list content
            item_lines = lines[index:end_index]

            # Remove the list markers
            list_content = [re.sub(regex_pattern, "", line) for line in item_lines]

            return instance_class(list_content), end_index

        return None


class UnorderedList(AbstractList):
    def list_type(self):
        return "itemize"

    @staticmethod
    def detect_block(
        lines: Sequence[str], index: int
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        return AbstractList.detect_block(lines, index, r"^-\s+", UnorderedList)


class OrderedList(AbstractList):
    def list_type(self):
        return "enumerate"

    @staticmethod
    def detect_block(
        lines: Sequence[str], index: int
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        return AbstractList.detect_block(lines, index, r"^\d+\.\s+", OrderedList)


class Quote(LaTeXBlock):
    def __init__(self, content):
        super().__init__(content)
        self.lines = content

    def formatted_text(self, **kwargs):
        content = "\\begin{displayquote}\n"

        for line in format_text(self.lines):
            content += f"\t{line}\n"

        content += "\\end{displayquote}\n"

        return content

    def __repr__(self):
        return f"Quote(content={self.content})"

    @staticmethod
    def detect_block(
        lines: Sequence[str], index: int
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        def _is_quote(line):
            return line.startswith(">")

        if _is_quote(lines[index]) and not any(
            v in lines[index] for v in SPECIAL_CALLOUTS
        ):
            end_index = find_next_index(
                lines, lambda line: not _is_quote(line), index + 1
            )
            quote_lines = lines[index:end_index]
            return Quote(quote_lines), end_index

        return None


class AbstractCallout(LaTeXBlock):
    def __init__(self, caption: str, lines: Sequence[str], configs: dict):
        super().__init__(lines)
        self.caption = caption.strip()
        self.lines = lines
        self.configs = configs

    def __repr__(self):
        return f'{self.__class__.__name__}(caption="{self.caption}", lines={self.lines}, configs={self.configs})'

    @staticmethod
    def detect_block(lines, index, callout: str, instance_class: Type["LaTeXBlock"]):
        callout_pattern = re.compile(f"^>\s*\[!{callout}\]\s*(.*)\s*")
        re_match = callout_pattern.match(lines[index])

        if re_match is not None:
            caption = re_match.group(1)
            end_index = find_next_index(
                lines, lambda line: not line.startswith(">"), index + 1
            )
            callout_lines = lines[index + 1 : end_index]

            # Remove config marker from all
            callout_lines = [l.replace(QUOTE_MARKER, "") for l in callout_lines]

            # Might contain configurations in the callout, need to confirm
            start_config_marker_index = find_next_index(
                callout_lines, lambda line: line.startswith(CALLOUT_CONFIG_MARKER), 0
            )

            if start_config_marker_index < len(callout_lines):
                # Then there could be properties
                end_config_marker_index = find_next_index(
                    callout_lines,
                    lambda line: line.startswith(CALLOUT_CONFIG_MARKER),
                    start_config_marker_index + 1,
                )
                config_lines = callout_lines[
                    start_config_marker_index + 1 : end_config_marker_index
                ]

                try:
                    configs = yaml.safe_load("\n".join(config_lines))
                except:
                    raise ValueError(
                        f"Could not parse configurations in callout ({callout}): {config_lines}"
                    )

                # Change the end of the call out lines
                callout_lines = callout_lines[:start_config_marker_index]
            else:
                configs = {}

            return instance_class(caption, callout_lines, configs), end_index


class Table(AbstractCallout):
    def __init__(self, caption: str, lines: Sequence[str], configs: dict):
        super().__init__(caption, lines, configs)

        try:
            import pandas as pd
        except:
            raise ImportError(
                "You defined a table, but pandas is not installed. Please install pandas to use tables."
            )

        # Parse the table
        table_content = "\n".join(format_text(self.lines))

        df = (
            pd.read_table(StringIO(table_content), sep="|", engine="python")
            .dropna(how="all", axis=1)
            .dropna(how="all")
        )

        # Clean up column names and content (strip leading/trailing whitespace)
        df.columns = df.columns.str.strip()
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        # Step 2: Filter out any rows filled with '----' (typically separators)
        df = df[~df.apply(lambda row: row.str.contains("----").any(), axis=1)]

        self.df = df

        # Check for latex specific configurations in the configs
        position = self.configs.get("position", None)
        column_format = self.configs.get(
            "column_format", "l" + "r" * (len(df.columns) - 1)
        )
        centering = self.configs.get("centering", True)

        self.latex_content = df.to_latex(
            index=False,
            caption=caption,
            position=position,
            column_format=column_format,
        )

        if centering:
            split_latex_content = self.latex_content.split("\n")
            split_latex_content.insert(1, "\\centering")
            self.latex_content = "\n".join(split_latex_content)

    def formatted_text(self, **kwargs):
        return self.latex_content

    @staticmethod
    def detect_block(
        lines: Sequence[str], index: int
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        return AbstractCallout.detect_block(lines, index, "table", Table)


class Figure(AbstractCallout):
    def __init__(self, caption: str, lines: Sequence[str], configs: dict):
        super().__init__(caption, lines, configs)
        self.target_image = re.match(r"\s*\!\[\[(.*?)\]\]", self.lines[0])

        if self.target_image is None:
            raise ValueError(f"Could not find image in callout: {self.lines[0]}")

        self.target_image = self.target_image.group(1)
        self.target_image = self.target_image.split("|")[0]
        self.target_image = self.target_image.split("/")[-1]

        # Figure latex configs
        self.label = self.configs.get("label", None)
        self.position = self.configs.get("position", None)
        self.centering = self.configs.get("centering", True)
        self.width = self.configs.get("width", 0.5)

    def formatted_text(self, **kwargs):
        graphics_foler: Optional[Path] = kwargs.get("graphics_folder", None)

        if graphics_foler is None:
            raise ValueError(
                "You defined a figure, but no graphics folder was provided."
            )

        image_path = (graphics_foler / self.target_image).resolve()

        if not image_path.exists():
            raise FileNotFoundError(f"Could not find image {image_path}")

        content = "\\begin{figure}"

        if self.position is not None:
            content += f"[{self.position}]"

        content += "\n"

        if self.centering:
            content += "\\centering\n"

        content += f"\\includegraphics[width={self.width}\\textwidth]{{{image_path}}}\n"

        # Format the caption, since it might contain citations
        caption = format_text([self.caption])[0]
        content += f"\\caption{{{caption}}}\n"

        if self.label is not None:
            content += f"\\label{{fig:{self.label}}}\n"

        content += "\\end{figure}\n"

        return content

    @staticmethod
    def detect_block(
        lines: Sequence[str], index: int
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        return AbstractCallout.detect_block(lines, index, "figure", Figure)


class AbstractCodeBlock(LaTeXBlock):
    def __init__(self, content: str, language: str, in_latex: bool = True):
        super().__init__(content, in_latex=in_latex)
        self.language = language

    def __repr__(self):
        return f'{self.__class__.__name__}(content="{self.content}", language="{self.language}")'

    @staticmethod
    def detect_block(
        lines: Sequence[str],
        index: int,
        language: str,
        instance_class: Type["LaTeXBlock"],
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        if lines[index].startswith(f"```{language}"):
            end_index = find_next_index(
                lines, lambda line: line.startswith("```"), index + 1
            )
            raw_lines = lines[index + 1 : end_index]
            return instance_class("\n".join(raw_lines), language), end_index

        return None


class RawLaTeXBlock(AbstractCodeBlock):
    @staticmethod
    def detect_block(
        lines: Sequence[str], index: int
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        return AbstractCodeBlock.detect_block(lines, index, "latex", RawLaTeXBlock)


class TikZBlock(AbstractCodeBlock):
    def formatted_text(self, **kwargs):
        self.content = self.content.replace("\\begin{document}", "")
        self.content = self.content.replace("\\end{document}", "")
        self.content = re.sub(r"\\usepackage.*\n", "", self.content)
        self.content = re.sub(r"\\usetikzlibrary.*\n", "", self.content)
        return super().formatted_text(**kwargs)

    @staticmethod
    def detect_block(
        lines: Sequence[str], index: int
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        return AbstractCodeBlock.detect_block(lines, index, "tikz", TikZBlock)


class PythonBlock(AbstractCodeBlock):
    def formatted_text(self, **kwargs):
        return f"\\begin{{lstlisting}}[language=Python]\n{self.content}\\end{{lstlisting}}\n"

    @staticmethod
    def detect_block(
        lines: Sequence[str], index: int
    ) -> Optional[Tuple["LaTeXBlock", int]]:
        return AbstractCodeBlock.detect_block(lines, index, "python", PythonBlock)


PARSEABLE_BLOCKS: Sequence[Type[LaTeXBlock]] = [
    Section,
    Equation,
    UnorderedList,
    OrderedList,
    Table,
    Quote,
    Figure,
    RawLaTeXBlock,
    TikZBlock,
    PythonBlock,
]
