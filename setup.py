"""
Package setup configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="anomaly-correction-agent",
    version="1.0.0",
    author="Google AI",
    author_email="ai-team@google.com",
    description="State-of-the-art anomaly detection and auto-correction agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/google/anomaly-correction-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "sentence-transformers>=2.2.0",
        "scikit-learn>=1.3.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "anomaly-agent=main:main",
        ],
    },
)