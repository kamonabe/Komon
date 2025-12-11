"""
Komon - 軽量アドバイザー型SOAR風監視ツール
セットアップスクリプト
"""

from setuptools import setup, find_packages
from pathlib import Path

# README.mdを読み込む
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# version.txtからバージョンを読み込む
version = (this_directory / "version.txt").read_text(encoding="utf-8").strip()

setup(
    name="komon",
    version=version,
    description="軽量アドバイザー型SOAR風監視ツール",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="kamonabe",
    url="https://github.com/kamonabe/Komon",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "psutil>=5.9.0",
        "PyYAML>=6.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "komon=komon.cli:main",
        ],
    },
    data_files=[
        ("config", ["config/settings.yml.sample"]),
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.9",
    include_package_data=True,
)

