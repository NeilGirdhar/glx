from distutils.core import setup


setup(
    name = 'glx',
    packages = ['glx'],
    version = '0.1',
    description = 'Classes that facilitate working with OpenGL 4.4 shaders and efficiently rendering text.',
    author = 'Neil Girdhar',
    author_email = 'mistersheik@gmail.com',
    url = 'https://github.com/NeilGirdhar/glx',
    download_url = 'https://github.com/neilgirdhar/glx/archive/0.1.tar.gz',
    keywords = [],
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
    install_requires = ['numpy>=1.13',
                        'mako>=1.0.7',
                        'rectangle>=0.2',
                        'freetype>=1.1',
                        'PyOpenGL>=3.0.0']
    python_requires='>=3.4',
)
