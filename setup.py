from setuptools import setup, find_packages

setup(
    name="git_contribution_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "matplotlib",
    ],
    author="Wavenet",
    description="A tool for analyzing git contributions across multiple repositories",
    python_requires=">=3.7",
)
