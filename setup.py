import setuptools

with open("requirements.txt", "r") as fr:
    installation_requirements = fr.readlines()

with open("README.md", "r") as fr:
    long_description = fr.read()

setuptools.setup(
    name="obsitex",
    version="0.0.4",
    author="Rui Reis",
    author_email="ruipedronetoreis12@gmail.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=installation_requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "obsitex=obsitex.cli:main",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="A Python package to convert Obsidian Markdown files and folders into structured LaTeX documents.",
)
