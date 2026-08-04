from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

from church_sms import __version__ as version

setup(
    name="church_sms",
    version=version,
    description="Church SMS Management System for Frappe/ERPNext",
    author="KODA Systems",
    author_email="justinemsengi@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
