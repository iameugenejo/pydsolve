from distutils.core import setup

setup(
    name='dsolve',
    package_dir={'': 'src'},
    version='1.0.0',
    platforms='any',
    description='Generic Dependency Resolver',
    author='Eugene Jo',
    author_email='iameugenejo@gmail.com',
    url='https://github.com/iameugenejo/pydsolve',
    install_requires=open('requirements.txt').readlines()
)
