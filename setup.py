from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from os.path import dirname, join
import sys



def main():
    base_dir = dirname(__file__)
    install_requires = ['boxsdk>=2.0.0a7']
    jwt_requires = ['boxsdk[jwt]']
    extra_requires = {'jwt': jwt_requires, 'all': (['boxsdk[all]'] + [jwt_requires])}
    setup(
        name='Ransomware File Rollback Tool',
        version="0.1.0",
        author="Rich Duchin",
        author_email="rduchin@box.com",
        description="Tool developed to mitigate ransomware compromised files by promoting the latest unencrypted file version, provided a time window of the attack is given.",
        url="https://github.com/Bullkn0x/ransomware-file-rollback",
        packages=find_packages(),
        install_requires=[
            "python-dotenv",
            "cryptography",
            "boxsdk",
            "iso8601",
            "rfc3339"

        ],
    )

if __name__ == '__main__':
    main()
