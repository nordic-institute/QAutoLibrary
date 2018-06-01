import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="QAutoLibrary",
    version="0.0.2",
    author="QAutomate",
    author_email="contact@qautomate.fi",
    description="QAutofamily testing framework library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QAutofamily/QAutoLibrary",
    packages=setuptools.find_packages(),
    package_data={'QAutoLibrary.config': ['*.xml', '*.ini']},
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent",
    ),
)
