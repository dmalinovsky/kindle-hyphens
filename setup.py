from setuptools import setup, find_packages

setup(name='fb2-hyphens',
  version='0.1',
  author='Denis Malinovsky',
  author_email='dmalinovsky@gmail.com',
  packages=find_packages(),
  include_package_data=True,
  description=open('README.md').read(),
  install_requires=open('requirements.txt').readlines(),
)
