import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="QAutoLibrary",
    version="0.0.1",
    author="QAutomate",
    author_email="contact@qautomate.fi",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QAutofamily/QAutoLibrary",
    packages=setuptools.find_packages(),
    package_data={'QAutoLibrary.config': ['*.xml', '*.ini']},
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)