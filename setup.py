"""
Based on https://python-packaging.readthedocs.io/en/latest/
"""

import os
import glob
import shutil
from setuptools import setup, find_packages, Command


class CompleteClean(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        shutil.rmtree('./build', ignore_errors=True)
        shutil.rmtree('./dist', ignore_errors=True)
        shutil.rmtree('./' + project + '.egg-info', ignore_errors=True)
        temporal = glob.glob('./' + project + '/*.pyc')
        for t in temporal:
            os.remove(t)


with open('requirements.txt', mode='r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

with open('README.md', mode='r', encoding='utf-8') as fh:
    long_description = fh.read()

project = 'partygroupcomp'
setup(
    name=project,
    version="1.0.0",
    author="Daniel de las Heras Montero",
    author_email="dherasmontero@gmail.com",
    description="Cryptografical group compiler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/danydlhm/2PartytoGroupCompiler",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements[::-1],
    cmdclass={'clean': CompleteClean},
    test_suite='nose.collector',
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.6',
)