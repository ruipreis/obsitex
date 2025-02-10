from pathlib import Path

from obsitex import ObsidianParser
from obsitex.parser.blocks import AbstractCallout, LaTeXBlock
from obsitex.parser.formatting import format_text


class LineBreakBlock(LaTeXBlock):
    def __init__(self):
        super().__init__("\\newpage", in_latex=True)

    @staticmethod
    def detect_block(lines, index):
        if lines[index].startswith("---"):
            return LineBreakBlock(), index + 1


class CustomWarningBlock(AbstractCallout):
    def formatted_text(self, **kwargs):
        content = "\n".join(format_text(self.content))

        return f"""
\\begin{{bclogo}}[logo=\\bcattention, couleurBarre=red, noborder=true, 
               couleur=LightSalmon]{{{self.caption}}}
{content}
\\end{{bclogo}}
"""

    @staticmethod
    def detect_block(lines, index):
        return AbstractCallout.detect_block(lines, index, "warning", CustomWarningBlock)


if __name__ == "__main__":
    # Define input and output paths
    base_path = Path(__file__).parent
    input_path = base_path / "Bring Your Own Blocks.md"
    output_path = base_path / "output" / "main.tex"
    template_path = base_path / "template.tex"

    # Load the template
    with open(template_path, "r") as f:
        template = f.read()

    # Create parser and add custom block
    parser = ObsidianParser(
        custom_blocks=[
            LineBreakBlock,
            CustomWarningBlock,
        ],
        main_template=template,
    )

    # Parse the input file
    parser.add_file(input_path)

    # Write the output file
    with open(output_path, "w") as f:
        f.write(parser.to_latex())
