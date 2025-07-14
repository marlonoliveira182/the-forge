"""
Setup script for The Forge v2.0.0 - Modern Desktop Application
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else "The Forge v2.0.0 - Modern Desktop Schema Conversion Tool"

# Read requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="the-forge",
    version="2.0.0",
    author="EDP Team",
    author_email="team@edp.com",
    description="Modern desktop schema conversion and mapping tool for XSD and JSON Schema",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/edp/the-forge",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Software Development :: Documentation",
        "Topic :: Desktop Environment :: Desktop Environment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "gui": [
            "PySide6>=6.5.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "build": [
            "PyInstaller>=5.13.0",
            "cx-Freeze>=6.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "the-forge-cli=src.cli.main:main",
        ],
        "gui_scripts": [
            "the-forge=src.gui.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.png", "*.ico", "*.qss"],
    },
    keywords="schema xsd json-schema conversion mapping excel desktop gui",
    project_urls={
        "Bug Reports": "https://github.com/edp/the-forge/issues",
        "Source": "https://github.com/edp/the-forge",
        "Documentation": "https://the-forge.readthedocs.io/",
    },
) 