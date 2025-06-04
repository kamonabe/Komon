# setup.py

from setuptools import setup, find_packages

setup(
    name="komon",
    version="1.2.2",
    description="軽量SOAR風アドバイザー Komon",
    author="kamonabe",
    packages=find_packages(),
    install_requires=[
        "psutil",      # リソース監視
        "PyYAML",      # settings.yml用
        # "matplotlib",  # CLIグラフ描画（必要なら）
    ],
    entry_points={
        "console_scripts": [
            "komon = komon.cli:main"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)

