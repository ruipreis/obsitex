import setuptools

with open("requirements.txt", "r") as fr:
    installation_requirements = fr.readlines()

setuptools.setup(
    name="obsitex",
    version="0.0.0",
    author="Rui Reis",
    author_email="ruipedronetoreis12@gmail.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "",
        "Operating System :: OS Independent",
    ],
    install_requires=installation_requirements,
    python_requires=">=3.8",
)