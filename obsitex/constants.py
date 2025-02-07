DEFAULT_JINJA2_JOB_TEMPLATE = "{{ parsed_latex_content }}"
DEFAULT_JINJA2_MAIN_TEMPLATE = DEFAULT_JINJA2_JOB_TEMPLATE
DEFAULT_HLEVEL_MAPPING = {
    -2: "part",
    -1: "chapter",
    0: "section",
    1: "subsection",
    2: "subsubsection",
    3: "paragraph",
}

# How markers are placed in parsed latex
DEFAULT_APPENDIX_MARKER = """
\\appendix
"""

DEFAULT_BIBLIOGRAPHY_MARKER = """
\\bibliography{references}
"""

SPECIAL_CALLOUTS = [
    "[!figure]",
    "[!table]",
    "[!chart]",
]

QUOTE_MARKER = "> "
CALLOUT_CONFIG_MARKER = "%%"
