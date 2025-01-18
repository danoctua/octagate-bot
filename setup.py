from setuptools import find_packages, setup

setup(
    name="octagate",
    version="2.0.0",
    description="Octagate Community Management Platform",
    author="danoctua",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "load-jetton = core.cli.load_jetton:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
