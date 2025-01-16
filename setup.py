from setuptools import find_packages, setup

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name='SingleSauce',
    packages=find_packages(exclude=['examples']),
    version='0.0.1',
    license='MIT',
    description='Code base for recipe organizer app',
    author='Torda Balázs',
    author_email='balazs.torda@iu-study.org',
    url='https://github.com/jurdabos/singlesauce',
    install_requires=requirements,
)