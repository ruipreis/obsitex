from pathlib import Path

from obsitex import ObsidianParser

AVAILABLE_SAMPLES = {
    "msc-dissertation": "obsidian-folder",
    "sock-research-paper": "The Evolution of Socks.md",
}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert Obsidian notes to LaTeX")
    parser.add_argument("sample", choices=AVAILABLE_SAMPLES, help="The sample to run")

    args = parser.parse_args()

    # Define input paths
    base_path = Path(__file__).resolve().parent
    content_path = base_path / args.sample / AVAILABLE_SAMPLES[args.sample]
    bibtex_database_path = base_path / "shared-references.bib"
    graphics_folder = base_path / args.sample / "images"
    template_path = base_path / args.sample / "template.tex"

    # Define output paths
    output_path = base_path / args.sample / "output" / "main.tex"
    output_path.parent.mkdir(exist_ok=True, parents=True)
    output_bibtex_path = output_path.parent / "main.bib"

    # Read the template and parse the content
    with open(template_path, "r") as file:
        template = file.read()

    parser = ObsidianParser(
        graphics_folder=graphics_folder,
        main_template=template,
        bibtex_database_path=bibtex_database_path,
        out_bitex_path=output_bibtex_path,
    )

    if content_path.is_dir():
        parser.add_dir(content_path)
    elif content_path.is_file():
        parser.add_file(content_path)
    else:
        raise ValueError(f"Invalid path: {content_path}")

    # Apply the jobs and write the output
    parser.apply_jobs()

    with open(output_path, "w") as file:
        file.write(parser.to_latex())

    print(f"Output written to {output_path}")
    print(f"You may go to the output directory and compile the LaTeX file manually")
