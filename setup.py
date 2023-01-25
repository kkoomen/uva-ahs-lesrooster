#!/usr/bin/env python3


from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name='lesrooster',
    version='1.0.0',
    author='Kim Koomen',
    author_email='koomen@pm.me',
    description='University Course Timetabling Problem with different algorithms',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kkoomen/uva-ahs-lesrooster',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=install_requires,
    python_requires='>=3.6',
)
