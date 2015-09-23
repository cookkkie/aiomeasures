#!/usr/bin/env python
from setuptools import setup, find_packages, Command
import versioneer


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys
        errno = subprocess.call([sys.executable,
                                 'runtests.py',
                                 'tests/',
                                 '--cov', '',
                                 '--cov-report', 'html'])
        raise SystemExit(errno)

cmds = versioneer.get_cmdclass()
cmds.update({'test': PyTest})

setup(
    name='AIOTow',
    version=versioneer.get_version(),
    description="Metrics metrics metrics",
    author="",
    author_email='clint.northwood@gmail.com',
    url='https://lab.errorist.xyz/abc/',
    packages=find_packages(),
    keywords=[''],
    install_requires=[],
    extras_require={
        ':python_version=="3.3"': ['asyncio'],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    license='MIT',
    cmdclass=cmds
)
