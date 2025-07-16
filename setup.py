from setuptools import setup, find_packages

setup(
    name='atlas-ai',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'atlas = atlas.cli:main',
        ],
    },
    install_requires=[
        'pylance',
        'pyarrow',
        'pandas',
        'click',
        'Pillow',
        'psutil',
        'matplotlib',
        'pyyaml'
    ],
)
