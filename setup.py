from setuptools import setup, find_packages

setup(
    name="docs-to-site",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "docs_to_site": ["resources/*"],
    },
    include_package_data=True,
    install_requires=[
        "setuptools>=42.0.0",
        "markitdown>=0.0.1a3",
        "mkdocs>=1.5.0",
        "mkdocs-material>=9.4.0",
        "python-slugify>=8.0.0",
        "python-pptx>=0.6.21",
        "scour>=0.38.2",
    ],
    entry_points={
        "console_scripts": [
            "docs-to-site=docs_to_site.__main__:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Convert various document formats into a hosted MkDocs site",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/docs-to-site",
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
    ],
    python_requires=">=3.8",
) 