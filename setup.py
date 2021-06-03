from setuptools import setup, find_packages

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='hamutils',
    version='0.2.1',
    description='Amateur radio utils library',
    long_description=long_description,
    url='https://github.com/sq8kfh/hamutils',
    download_url='https://github.com/sq8kfh/hamutils/tarball/v0.2.1',
    author='SQ8KFH',
    author_email='sq8kfh@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Ham Radio',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='ham qrz space weather adif adi adx cabrillo',
    packages=find_packages(),
    python_requires='>=3.4',
    install_requires=[
        'unidecode',
    ],

    # $ pip install -e .[dev,test]
    # extras_require={
    #    'testing': ['pytest'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'sample': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)
