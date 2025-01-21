from setuptools import find_packages, setup

setup(
    name="octagate",
    version="2.0.0",
    description="Octagate Community Management Platform",
    author="danoctua",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "load-wallets-on-start = core.cli.load_wallets_on_start:main",
            "load-telegram-chat = core.cli.load_telegram_chat:main",
            "load-jetton = wallet_indexer.cli.load_jetton:main",
            "load-nft-collection = wallet_indexer.cli.load_nft_collection:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
