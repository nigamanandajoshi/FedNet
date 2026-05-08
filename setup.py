from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fednet",
    version="0.1.0",
    author="Nigamananda Joshi",
    author_email="nigamanandajoshi@gmail.com",
    description="Governance, auditability, and monetization layer for federated learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nigamanandajoshi/FedNet",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "pydantic>=2.4.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "full": [
            "torchvision>=0.15.0",
            "pandas>=2.0.0",
            "scikit-learn>=1.3.0",
            "flower>=1.5.0",
            "matplotlib>=3.8.0",
            "seaborn>=0.13.0",
            "plotly>=5.17.0",
            "tensorboard>=2.14.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fednet-train=scripts.run_local_fl:main",
            "fednet-generate=scripts.generate_demo_data:main",
        ],
    },
)
