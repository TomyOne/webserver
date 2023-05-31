#!/usr/bin/env python3
"""webserver setup script."""
import os

from setuptools import setup, find_packages

PROJECT_NAME = "webserver"
PROJECT_PACKAGE_NAME = "webserver"
PROJECT_LICENSE = "MIT"
PROJECT_AUTHOR = "Tomas Galbicka"
PROJECT_COPYRIGHT = "2023, Webserver"
PROJECT_URL = "https://skaro.sk/"
PROJECT_EMAIL = "info@skaro.sk"

PROJECT_GITHUB_USERNAME = "tomyone"
PROJECT_GITHUB_REPOSITORY = "webserver"

PYPI_URL = f"https://pypi.python.org/pypi/{PROJECT_PACKAGE_NAME}"
GITHUB_PATH = f"{PROJECT_GITHUB_USERNAME}/{PROJECT_GITHUB_REPOSITORY}"
GITHUB_URL = f"https://github.com/{GITHUB_PATH}"

DOWNLOAD_URL = f"{GITHUB_URL}/archive/v0.0.1.zip"

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "requirements.txt")) as requirements_txt:
    REQUIRES = requirements_txt.read().splitlines()

with open(os.path.join(here, "README.md")) as readme:
    LONG_DESCRIPTION = readme.read()

CLASSIFIERS = [
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Topic :: Web Servers",
]

setup(
    name=PROJECT_PACKAGE_NAME,
    version="0.0.1",
    license=PROJECT_LICENSE,
    url=GITHUB_URL,
    project_urls={
        "Bug Tracker": "#",
        "Feature Request Tracker": "#",
        "Source Code": "#",
        "Documentation": "#",
        "Twitter": "#",
    },
    download_url=DOWNLOAD_URL,
    author=PROJECT_AUTHOR,
    author_email=PROJECT_EMAIL,
    description="Webserver based on tornado.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    # test_suite="tests",
    python_requires=">=3.9.0",
    install_requires=REQUIRES,
    keywords=["web", "webserver"],
    entry_points={"console_scripts": ["webserver = webserver.__main__:main"]},
    packages=find_packages(include="webserver.*"),
)
