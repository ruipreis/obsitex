from pathlib import Path

from obsitex.parser import ObsidianParser

# Input paths
paper_path = Path(__file__).parent / "The Evolution of Socks.md"
graphics_folder = Path(__file__).parent / "images"

# Output paths
output_path = Path(__file__).parent / "output" / "main.tex"
output_path.parent.mkdir(exist_ok=True, parents=True)

parser = ObsidianParser(graphics_folder=graphics_folder)
parser.add_file(paper_path)

parser.apply_jobs()

text = parser.to_latex()

with open(output_path, "w") as file:
    file.write(text)
