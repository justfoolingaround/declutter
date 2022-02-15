from setuptools import setup, find_packages
from declutter import __version__

setup(
    name="declutter",
    version=__version__,
    author="kr@justfoolingaround",
    author_email="kr.justfoolingaround@gmail.com",
    description="An ultimate file organising tool for your directories.",
    packages=find_packages(),
    url="https://github.com/justfoolingaround/declutter",
    install_requires=[
        "click",
        "regex==2021.10.8",
        "rich",
    ],
    entry_points="""
        [console_scripts]
        declutter=declutter.__main__:__declutter_cli__
    """,
)
