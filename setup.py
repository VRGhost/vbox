import os
from distutils.core import setup

def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
        )

def find_packages(path, base="" ):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package( dir ):
            if item.lower() == "tests":
                # Ignore 'tests' packages
                continue
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages

setup(name='vbox',
    version='0.1.2',
    description="VirtualBox CLI bindings",
    long_description=open("README.md").read(),

    author="Ilja Orlovs",
    author_email="vywn@gryyf.fb".decode("rot13"),
    url='https://github.com/VRGhost/vbox',
    packages=find_packages("src"),
    package_dir = {'': 'src'},

    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ])
