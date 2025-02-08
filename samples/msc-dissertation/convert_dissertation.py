from pathlib import Path

from obsitex.parser import ObsidianParser

# Input paths
paper_path = Path(__file__).parent / "obsidian-folder"
graphics_folder = Path(__file__).parent / "images"
bibtex_database_path = Path(__file__).resolve().parent.parent / "shared-references.bib"

# Output paths
output_path = Path(__file__).parent / "output" / "main.tex"
output_path.parent.mkdir(exist_ok=True, parents=True)
output_bibtex_path = output_path.parent / "main.bib"

# The parser should generate a working LaTeX file, so we use the
# template.tex jinja2 latex template file to generate the output,
# the parser will implictly replace the 'parsed_latex_content' block
template_file = Path(__file__).parent / "template" / "template.tex"

with open(template_file, "r") as file:
    template = file.read()

parser = ObsidianParser(
    graphics_folder=graphics_folder,
    main_template=template,
    bibtex_database_path=bibtex_database_path,
    out_bitex_path=output_bibtex_path,
)
parser.add_dir(paper_path)

parser.apply_jobs()

text = parser.to_latex()

with open(output_path, "w") as file:
    file.write(text)
