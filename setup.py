"""
Setup script for AgentHansa SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agenthansa",
    version="0.1.0",
    author="Zero Human Company",
    author_email="",
    description="Official Python SDK for the AgentHansa API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agenthansa-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
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
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "mypy>=0.950",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agenthansa=agenthansa.cli:main",
        ],
    },
)
