from obsitex.planner import ExecutionPlan
from obsitex.parser import MarkdownJobParser
from pathlib import Path

import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    test_dir = Path(
        "/home/ruipreis/Documents/second-brain/Archive/Academia/Thesis/Writing"
    )
    biblio_path = Path(
        "/home/ruipreis/Documents/second-brain/Resources/Bibliography/zotero-lib.bib"
    )
    graphics_folder = Path(
        "/home/ruipreis/Documents/second-brain/Resources/Attachments"
    )

    plan = ExecutionPlan(bibtex_database_path=biblio_path)
    plan.add_dir(test_dir)

    plan.show(show_configs=True)

    parser = MarkdownJobParser(
        graphics_folder=graphics_folder,
    )
    for job in plan.iter_jobs():
        parser.parse_job(job)

    text = parser.to_latex()

    with open("test.tex", "w") as file:
        file.write(text)
