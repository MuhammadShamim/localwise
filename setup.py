"""Setup configuration for LocalWise - AI Knowledge Assistant."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="localwise",
    version="1.0.0",
    author="LocalWise Development Team",
    author_email="dev@localwise.ai",
    description="Your AI Knowledge Assistant - Transform documents into intelligent, searchable knowledge bases entirely offline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/localwise/localwise",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: General",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'pre-commit>=3.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.2.0',
            'myst-parser>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'localwise=localwise.cli.cli_interface:main',
            'localwise-process=localwise.cli.cli_interface:process_command',
            'localwise-serve=localwise.cli.cli_interface:serve_command',
        ],
    },
    include_package_data=True,
    package_data={
        'localwise': [
            'data/*.json',
            'ui/templates/*.html',
            'cli/examples/*.txt',
        ],
    },
    keywords=[
        "ai", "knowledge-base", "document-processing", "rag", "llm",
        "local-ai", "privacy", "offline", "embeddings", "search",
        "streamlit", "ollama", "vectors", "nlp", "text-processing"
    ],
    project_urls={
        "Documentation": "https://github.com/localwise/localwise/wiki",
        "Bug Reports": "https://github.com/localwise/localwise/issues",
        "Source Code": "https://github.com/localwise/localwise",
        "Changelog": "https://github.com/localwise/localwise/blob/main/CHANGELOG.md",
    },
    zip_safe=False,
    platforms=['any'],
    license="MIT",
)