import setuptools
from app.settings import settings

with open("README.md", "r", encoding="utf-8") as fh:
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
    install_requires = [
        'python-dotenv==0.15.0',
        'requests==2.25.0',
        'numpy==1.19.3',
        'scipy==1.5.4',
        'matplotlib==3.3.3',
        'holidays==0.10.4'
        'PyQt5==5.15.2'
    ],
    entry_points={
        "console_scripts": [
            "pynance = pynance:main"
        ]
    },
    classifers=[
        "Programming Language :: Python :: 3",
        "License:: GNU GPL v3",
        "Operating System :: OS Independent"
    ],
    python_requires = '>=3.8.7'
)