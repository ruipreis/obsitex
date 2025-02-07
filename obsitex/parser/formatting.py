import re
import copy
from typing import Optional

LATEX_SPECIAL_CHARS = r"$%_}&#{"

def find_next_index(lst, expr, start=0):
    for i in range(start, len(lst)):
        if expr(lst[i]):
            return i
    return len(lst)

def detect_command(line) -> Optional[str]:
    match = re.match(r"\%\%\s*(.*)\s*\%\%", line)
    command = None

    if match is not None:
        command = match.group(1)

    return command


# Function to group citations and replace
def replace_adjacent_citations(text):
    # Regex pattern to match adjacent citations
    pattern_adjacent = r"(\[\[@[^\]]+?\]\](\s*,\s*)*)*\[\[@[^\]]+?\]\]"

    # Find all matches for adjacent citations
    matches = re.finditer(pattern_adjacent, text)

    # Process each match
    for match in matches:
        # Extract the full matched string (group of adjacent citations)
        full_match = match.group(0)

        # Extract individual citations and combine them
        citations = re.findall(r"\[\[@([^\]]+?)\]\]", full_match)
        combined_citations = ",".join(citations)

        # Replace the full matched string with the combined citations
        text = text.replace(full_match, f"\\citep{{{combined_citations}}}")

    return text


def format_text(text_lines_origin):
    # Inspired by Alejandro Daniel Noel
    # In his code https://github.com/adanielnoel/Obsidian-to-latex/blob/master/parser_utils.py
    # Modified by me to fit the needs of this project
    text_lines = copy.deepcopy(text_lines_origin)

    for i in range(len(text_lines)):
        # ===== SPECIAL CHARACTERS =====
        # Extract and replace by placeholders equations and links before making formatting
        equations = re.findall(r"\$.*?\$", text_lines[i])
        links = re.findall(r"\[\[.*?]]", text_lines[i])
        codes = re.findall(r"`.*?`", text_lines[i])
        text_lines[i] = re.sub(r"\$.*?\$", "<EQ-PLACEHOLDER>", text_lines[i])
        text_lines[i] = re.sub(r"\[\[.*?]]", "<LINK-PLACEHOLDER>", text_lines[i])
        text_lines[i] = re.sub(r"`.*?`", "<CODE-PLACEHOLDER>", text_lines[i])
        # Format special chars that need to be escaped
        for special_char in LATEX_SPECIAL_CHARS:
            text_lines[i] = text_lines[i].replace(special_char, f"\\{special_char}")
        # Put square brackets in a group so that they are not parsed in latex as block arguments
        text_lines[i] = re.sub(r"(?<!\[)(\[.*])(?!])", r"{\1}", text_lines[i])
        # put back equations and links
        for link in links:
            text_lines[i] = text_lines[i].replace(r"<LINK-PLACEHOLDER>", link, 1)
        for equation in equations:
            text_lines[i] = text_lines[i].replace(r"<EQ-PLACEHOLDER>", equation, 1)
        for code in codes:
            text_lines[i] = text_lines[i].replace(r"<CODE-PLACEHOLDER>", code, 1)

        # Replace Markdown figure references by Latex references
        text_lines[i] = re.sub(r"`(fig:\S*?)`", r"\\autoref{\1}", text_lines[i])
        # Replace Markdown equation references by Latex references
        text_lines[i] = re.sub(r"`(eq:\S*?)`", r"\\autoref{\1}", text_lines[i])
        # Replace the markdown algorithm references by Latex references
        text_lines[i] = re.sub(r"`(alg:\S*?)`", r"\\autoref{\1}", text_lines[i])

        # ===== TEXT FORMATTING =====
        # Replace Markdown monospace by latex monospace (note: do after other code blocks like refs and citations)
        text_lines[i] = re.sub(r"`(.*?)`", r"\\texttt{\1}", text_lines[i])
        # Replace Markdown italics with quote marks by Latex text quote
        text_lines[i] = re.sub(
            r'(?<!\*)\*"([^\*].*?)"\*(?!\*)', r"\\textquote{\1}", text_lines[i]
        )
        # Replace Markdown italics by Latex italics
        text_lines[i] = re.sub(
            r"(?<!\*)\*([^\*].*?)\*(?!\*)", r"\\textit{\1}", text_lines[i]
        )
        # Replace Markdown bold by Latex bold
        text_lines[i] = re.sub(r"\*\*([^\*].*?)\*\*", r"\\textbf{\1}", text_lines[i])
        # Replace Markdown highlight by Latex highlight
        text_lines[i] = re.sub(r"==([^=].*?)==", r"\\hl{\1}", text_lines[i])
        text_lines[i] = replace_adjacent_citations(text_lines[i])

    return text_lines
