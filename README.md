# ObsiTex: Convert Obsidian Notes to LaTeX

ObsiTex is a Python package that automates the conversion of Obsidian Markdown files and folders into structured LaTeX documents. Designed for researchers, students, and technical writers, it ensures a seamless transition from Markdown to a fully formatted LaTeX file, preserving document structure and references.

![](https://raw.githubusercontent.com/ruipreis/obsitex/refs/heads/main/samples/images/banner.png)

## Why Use ObsiTex?

- Eliminates **manual LaTeX formatting** for Markdown-based notes.
- Preserves headings, lists, equations, figures, citations, and more.
- Supports **entire folders**, making it ideal for research papers and dissertations.
- Uses **Jinja2 templates**, allowing full customization of the LaTeX output.


## Table of Contents

- [Quick Start](#quick-start)
- [Supported Elements](#supported-elements)
  - [Citations](#citations)
  - [Callouts](#callouts)
    - [Figure](#figure)
    - [Table](#table)
    - [Styling](#styling)
- [Samples](#samples)
  - [Single File - Motivation Letter](#single-file---motivation-letter-for-willy-wonkas-chocolate-factory)
  - [Single File - Research Paper on Socks](#single-file---research-paper-on-socks)
  - [Folder - MSc Thesis on Ducks](#folder---msc-thesis-on-ducks)
  - [Bring Your Own Blocks](#bring-your-own-blocks)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Quick Start

To install ObsiTex, use pip:

```sh
pip install obsitex
```

Convert an Obsidian folder into a LaTeX document:

```sh
obsitex --input "My Obsidian Folder" --main-tex output.tex
```

Convert a single Markdown file:

```sh
obsitex --input "My Note.md" --main-tex output.tex
```

Use ObsiTex as a Python library:

```python
from obsitex import ObsidianParser

parser = ObsidianParser()
parser.add_dir("My Obsidian Folder")

latex_content: str = parser.to_latex()
```

## Supported Elements

Most of the standard Markdown elements are supported, including: 
- Equations (inline and block)
- Figures (with captions and metadata)
- Tables (with captions and metadata)
- Citations (using BibTeX references)
- Headings (up to level 6, but can be customized)
- Lists (enumerated and bulleted)
- Blockquotes
- Standard text formatting (bold, italics, code blocks, etc.)

### Citations

This system works best if used with the Obsidian plugin [obsidian-citation-plugin](https://github.com/hans/obsidian-citation-plugin), which allows for the easy insertion of citations in markdown files. The citations must be in the format `[[@citekey]]`, where `citekey` is the key of the reference in the BibTeX file.

### Callouts

#### Figure

Use the following syntax to create a figure in Obsidian:

```md
> [!figure] Caption for the figure
> ![[example-image.png]]
> %%
> width: 0.5
> label: example-image
> position: H
> %%
```

Which may be broken down as follows:
- `Caption for the figure`: The caption for the figure.
- `![[example-image.png]]`: The path to the image, if a figure is present, then the graphics folder must be provided.
- `%%`: This is a Obsidian comment, which allows for additional metadata to be added to the figure, without affecting the markdown rendering in Obsidian. If not present, default values will be used. This content must be YAML formatted.

#### Table

Use the following syntax to create a table in Obsidian:

```md
> [!table] Random Table
> | Name  | Age | City     |
> |-------|-----|----------|
> | Alice | 25  | New York |
> | Bob   | 30  | London   |
> | Eve   | 28  | Tokyo    |
> %%
> prop: value
> %%
```

This allows for the creation of tables in markdown, thus easily rendered in Obsidian, and then converted to LaTeX.

Similarly to figures, metadata can be added to the table, in order to customize the rendering of the table in LaTeX. This content must be YAML formatted.

#### Styling

These are custom blocks, thus won't have styling in Obsidian unless explictly defined in a CSS snippet. You can define the styling by following the instructions in the [Obsidian documentation](https://help.obsidian.md/Editing+and+formatting/Callouts#Customize+callouts). 


## Samples

- [Motivation Letter](#single-file---motivation-letter-for-willy-wonkas-chocolate-factory): Single file motivation letter with no citations or figures, one of the simplest use cases.
- [Sock Research Paper](#single-file---research-paper-on-socks): Single file research paper on socks with authors, affilitions, abstract, and content defined entirely in markdown.
- [MSc Dissertation on Ducks](#folder---msc-thesis-on-ducks): Folder containing a MSc thesis on ducks, with multiple markdown files under a common folder, and an `Index.md` file defining the hierarchy of the thesis.

These samples were all converted to PDF using XeLaTeX, and the output files are available in the `output` folder of each sample.

### Single File - Motivation Letter for Willy Wonka's Chocolate Factory

Charlie Beckett is applying for a position at Willy Wonka's Chocolate Factory, and has written a motivation letter in markdown. Of course this isn't the only factory he's applying to, so he wants the letter to be easily customizable for other applications.


Unlike the other examples, this example doesn't require a BibTex file or graphics folder, as it doesn't contain any citations or figures. The LaTeX file can be generated by:

```bash
cd samples/motivation-letter;

obsitex --input "Motivation Letter.md" \
    --template template.tex \
    --main-tex output/main.tex ;
```

#### Output Files

- [main.tex](https://github.com/ruipreis/obsitex/tree/main/samples/motivation-letter/output/main.tex)
- [main.pdf](https://github.com/ruipreis/obsitex/tree/main/samples/motivation-letter/output/main.pdf)


### Single File - Research Paper on Socks

Made up authors from the International Sock Research Institute, Textile Innovation Center, and Academy of Footwear Sciences have written a research paper on socks that was entirely developed in markdown. The authors now want to convert this document to pdf in order to submit it to a conference.

The LaTeX file and correspondings Bib file can be generated by:

```bash
cd samples/sock-research-paper;

obsitex --input "The Evolution of Socks.md" \
    --graphics ../images \
    --bibtex ../shared-references.bib \
    --template template.tex \
    --main-tex output/main.tex \
    --main-bibtex output/main.bib ;
```

#### Output Files

- [main.tex](https://github.com/ruipreis/obsitex/tree/main/samples/sock-research-paper/output/main.tex)
- [main.bib](https://github.com/ruipreis/obsitex/tree/main/samples/sock-research-paper/output/main.bib)
- [main.pdf](https://github.com/ruipreis/obsitex/tree/main/samples/sock-research-paper/output/main.pdf)

### Folder - MSc Thesis on Ducks

An unknown author has written a MSc thesis on ducks, and has organized the thesis in multiple markdown files under a common folder. The author now wants to convert this thesis to a single LaTeX file.

The folder structure is as follows:


```
obsidian-folder
├── Findings and Implications
│   ├── Conclusion
│   │   └── Conclusion.md
│   ├── Findings and Discussion
│   │   ├── Economic Viability.md
│   │   ├── Findings and Discussion.md
│   │   ├── Social and Cultural Implications.md
│   │   └── Urban Planning and Infrastructure Challenges.md
│   └── Findings and Implications.md
├── Index.md
└── Introduction and Background
    ├── Introduction
    │   └── Introduction.md
    ├── Introduction and Background.md
    ├── Literature Review
    │   └── Literature Review.md
    └── Methodology
        └── Methodology.md

8 directories, 11 files
```

`Index.md` defines the entry point for `obsitex`, by creating links between the different sections of the thesis, in the target order. In this example, the `Index.md` file is as follows:

```markdown
[[Introduction and Background]]

[[Findings and Implications]]
```

Thus, the first part will be the `Introduction and Background` part, followed by the `Findings and Implications` part. The LaTeX file and correspondings Bib file can be generated by:

```bash
cd samples/msc-dissertation;

obsitex --input obsidian-folder \
    --graphics ../images \
    --bibtex ../shared-references.bib \
    --template template.tex \
    --main-tex output/main.tex \
    --main-bibtex output/main.bib ;
```

#### Output Files

- [main.tex](https://github.com/ruipreis/obsitex/tree/main/samples/msc-dissertation/output/main.tex)
- [main.bib](https://github.com/ruipreis/obsitex/tree/main/samples/msc-dissertation/output/main.bib)
- [main.pdf](https://github.com/ruipreis/obsitex/tree/main/samples/msc-dissertation/output/main.pdf)

### Bring Your Own Blocks

Learn how to create parsers for custom blocks in the `samples/byob` folder. This will allow you to add custom blocks to the parser, and thus customize the LaTeX output to your needs.

This example adds support for line breaks and warnings in the LaTeX output, by creating custom blocks for these elements.

You can only use this feature if using the python library. To run this sample, use the following command:

```bash
cd samples/byob;

python run_sample.py;
```

#### Output Files

- [main.tex](https://github.com/ruipreis/obsitex/tree/main/samples/byob/output/main.tex)
- [main.pdf](https://github.com/ruipreis/obsitex/tree/main/samples/byob/output/main.pdf)

## Acknowledgments

This work was inspired by:
- [Obsidian Citation Plugin](https://github.com/hans/obsidian-citation-plugin) – For enabling seamless reference management within Obsidian.
- [Alejandro Daniel Noel](https://github.com/adanielnoel/Obsidian-to-latex) – His work served as an initial and valuable basis for this project.
- [dbt](https://github.com/dbt-labs/dbt-core) – For giving me the idea of using Jinja2 templates for LaTeX conversion.

## License

This project is licensed under the MIT License.
