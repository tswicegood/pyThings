from distutils.core import setup
import os

# Borrowed and modified from django-registration
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

def build_package(dirpath, dirnames, filenames):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    pkg = dirpath.replace(os.path.sep, '.')
    if os.path.altsep:
        pkg = pkg.replace(os.path.altsep, '.')
    packages.append(pkg)

[build_package(dirpath, dirnames, filenames) for dirpath, dirnames, filenames in os.walk('things')]

setup(
    name='pythings',
    version='0.1', # TODO: move this into Dolt.get_version()
    description='Simple wrapper around Things\'s AppleScript interface',
    author='Travis Swicegood',
    author_email='travis@domain51.com',
    url='http://github.com/tswicegood/pyThings/',
    packages=packages,
    install_requires=[
        "appscript",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Common Development and Distribution License (CDDL)',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)'
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
    ],
)

