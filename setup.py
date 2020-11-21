from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='orch',
    version='0.0.1',
    description='Orch lightweight container orchestrator.',
    long_description=readme,
    author='Gustavo de Lima',
    author_email='gusdlim@gmail.com',
    url='https://github.com/glimsil/orch',
    license=license,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=["click"],
    entry_points={
        'console_scripts': [ 
        'orch=main:cli' 
        ] 
    }
)