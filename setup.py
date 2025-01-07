from setuptools import setup, find_packages

setup(
    name="docs-to-site",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"": ["py.typed"]},
    install_requires=[
        "markitdown==0.0.1a3",
        "mkdocs>=1.4.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
        "typing-extensions>=4.0.0",
        "python-slugify>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "docs-to-site=docs_to_site.__main__:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to convert various document formats into a hosted MkDocs site",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Docs-to-Site",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
) 