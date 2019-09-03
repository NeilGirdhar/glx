#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='glx',
    version='0.6',
    description=('Classes that facilitate working with OpenGL 4.4 shaders '
                 'and efficiently rendering text.'),
    author='Neil Girdhar',
    author_email='mistersheik@gmail.com',
    project_urls={
        "Bug Tracker": "https://github.com/NeilGirdhar/glx/issues",
        "Source Code": "https://github.com/NeilGirdhar/glx",
    },
    download_url="https://pypi.python.org/pypi/glx",
    packages=find_packages(),
    package_data={
        'glx': ['**/*.vert', '**/*.frag', '**/*.geom'],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords=['OpenGL'],
    install_requires=['numpy>=1.13',
                      'mako>=1.0.7',
                      'rectangle>=0.2',
                      'freetype-py>=1.1',
                      'PyOpenGL>=3.0.0'],
    python_requires='>=3.7',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
