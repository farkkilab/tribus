import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tribus-jcasado", # Replace with your own username
    version="0.0.1",
    author="Julia Casado",
    author_email="julia.casado@helsinki.fi",
    description="Cell type based analysis of multiplexed imaging data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/farkkilab/tribus",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)