from setuptools import setup, find_packages

setup(
    name="medintel-fda",
    version="0.1.0",
    description="MedIntelAI: MedlinePlus & OpenFDA Explorer",
    author="Dipankar Bhowmik",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={
        "console_scripts": [
            "medintel=medintel.app:main"
        ],
    },
)
