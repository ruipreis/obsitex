import argparse
import logging
from pathlib import Path

from obsitex import ObsidianParser
from obsitex.constants import DEFAULT_JINJA2_MAIN_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="Convert Obsidian notes to LaTeX")

    # Defines the inputs
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Path to the input file or folder containing the Obsidian notes.",
        required=True,
    )

    parser.add_argument(
        "--bibtex",
        "-b",
        type=Path,
        help="Path to the BibTeX database file with all references.",
    )
    parser.add_argument(
        "--graphics",
        "-g",
        type=Path,
        help="Path to the graphics folder, where all images are assumed to be stored.",
    )
    parser.add_argument(
        "--template",
        "-t",
        type=Path,
        help="Path to the Jinja2 LaTeX template, won't use template if not provided.",
    )

    # Defines the outputs
    parser.add_argument(
        "--main-tex",
        "-mt",
        type=Path,
        help="Path to the LaTeX file that will be generated, containing all compiled LaTeX.",
        required=True,
    )
    parser.add_argument(
        "--main-bibtex",
        "-mb",
        type=Path,
        help="Path to the BibTeX file that will be generated, containing the references - only generated if citations are used.",
    )

    # Administrative options
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug mode, which will print additional information by enabling logging.",
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if not args.input.exists():
        raise FileNotFoundError(f"Input path {args.input} does not exist.")

    # Read the template if it exists
    if args.template is not None and args.template.is_file():
        with open(args.template, "r") as file:
            template = file.read()
        logging.info(f"Using template from {args.template}.")
    else:
        template = DEFAULT_JINJA2_MAIN_TEMPLATE
        logging.info("No template provided, using default template.")

    # Create the parser
    parser = ObsidianParser(
        graphics_folder=args.graphics,
        main_template=template,
        bibtex_database_path=args.bibtex,
        out_bitex_path=args.main_bibtex,
    )

    if args.input.is_dir():
        parser.add_dir(args.input)
    elif args.input.is_file():
        parser.add_file(args.input)
    else:
        raise ValueError(f"Invalid path: {args.input}")

    with open(args.main_tex, "w") as file:
        file.write(parser.to_latex())

    print(f"Output written to {args.main_tex}")


if __name__ == "__main__":
    main()
