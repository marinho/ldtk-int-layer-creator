import pathlib
from setuptools import setup

# The directory containing this file
CURDIR = pathlib.Path(__file__).parent

# The text of the README file
README = (CURDIR / "README.md").read_text()

setup(
    name='ldtk_intgrid_creator',
    version='0.2.0',
    description='Tool to generate IntGrid level for LDtk projects',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/marinho/ldtk-int-layer-creator',
    author='Marinho Brandao',
    author_email='marinho@gmail.com',
    license='LGPL',
    classifiers=[
        "License :: OSI Approved :: LGPL License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=['ldtk_intgrid_creator'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "create_int_level=ldtk_intgrid_creator.__main__:main",
        ]
    },
)
