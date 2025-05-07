# setup.py
from setuptools import setup

setup(
    name='disk-tree-cli',
    version='0.2.0',
    author='Karan5352',
    author_email='you@example.com',
    description='CLI tool to display disk usage as a color-coded tree',
    py_modules=['disk_tree'],
    install_requires=[
        'colorama>=0.4.6',
        'humanize>=4.9.0',
    ],
    entry_points={
        'console_scripts': [
            'dtree = disk_tree:main',        # shortened command
        ],
    },
    url='https://github.com/your-username/disk-tree-cli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
