import re
from typing import Any, Sequence, Set, Tuple


def find_all_citations(text: str) -> Set[Any]:
    # Regex pattern to match each citation tag
    citation_pattern = r"\[\[@([^\]]+?)\]\]"
    matches = re.findall(citation_pattern, text)

    # Return a set of unique citation keys
    return set(matches)


def find_all_links(text: str) -> Tuple[str, Sequence[str]]:
    link_regex = r"(?<!\!)\[\[(.*?)\]\]"
    all_links = re.findall(link_regex, text)

    # Filter out links starting with @, which are used for citations
    all_links = [link for link in all_links if not link.startswith("@")]
    resulting_links = []

    for link in all_links:
        if "|" in link:
            resulting_links.append(link.split("|")[1])
        elif "/" in link:
            resulting_links.append(link.split("/")[-1])
        else:
            resulting_links.append(link)

    # Remove links from original text
    for link in all_links:
        text = text.replace(f"[[{link}]]", "")

    text = text.strip()

    return text, resulting_links
