import os
from setuptools import setup, find_packages

this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, "README.md"), "r") as f:
    long_description = f.read()

setup(
    name="pyndows",
    version=open("pyndows/version.py").readlines()[-1].split()[-1].strip("\"'"),
    description="Accessing Windows from Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["test"]),
    install_requires=["pysmb==1.*"],
    extras_require={
        "testing": [
            # Used to manage testing
            "pytest==5.*"
        ]
    },
    python_requires=">=3.6",
    project_urls={
        "Changelog": "https://github.tools.digital.engie.com/gempy/pyndows/blob/master/CHANGELOG.md",
        "Issues": "https://github.tools.digital.engie.com/gempy/pyndows/issues",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Build Tools",
    ],
    keywords=["windows", "samba", "linux", "remote"],
    platforms=["Windows", "Linux"],
)
