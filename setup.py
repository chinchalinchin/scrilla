import setuptools
from app.settings import settings

with open("README.txt", "r", encoding="utf"-8) as fh:
    long_description = fh.read()

setuptools.setup(
    name=settings.APP_NAME,
    version=settings.VERSION,
    author="Grant Moore",
    author_email="chinchalinchin@gmail.com",
    description="A portfolio optimization application.",
    long_description=long_description,
    long_description_content_type="text/raw",
    url="https://github.com/chinchalinchin/pynance",
    packages=setuptools.find_packages(),
    classifers=[
        "Programming Language :: Python :: 3",
        "License:: GNU GPL",
        "Operating System :: OS Independent"
    ],
    python_requires = '==3.7.7'
)