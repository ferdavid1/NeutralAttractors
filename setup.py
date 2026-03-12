"""
Setup script for NeutralAttractors package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="neutralattractors",
    version="1.0.0",
    author="NeutralAttractors Research Team",
    description="Dynamical System Analysis for Super Smash Bros. Melee",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/NeutralAttractors",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "py-slippi>=1.5.1",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "pandas>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "neutralattractors=example_analysis:main",
        ],
    },
)
