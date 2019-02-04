from setuptools import setup

requires = [
    'docopt',
    'bs4',
    'python-dateutil',
    'aiohttp',
    'chromedriver-binary',
    'PyPOM',
    'selenium'
]

setup(
    name='krunk-copy',
    version='0.1.1',
    description='A utility that allows you to download pdfs '
                'based on collection_ids',
    long_description='',
    url='https://github.com/openstax/krunk-copy',
    license='AGPLv3',
    author='m1yag1',
    author_email='qa@openstax.org',
    py_modules=['krunk_copy'],
    install_requires=requires,
    zip_safe=False,
    entry_points={
        'console_scripts': ['kcopy=src.cli:cli']
    },
    classifiers=[],
)
