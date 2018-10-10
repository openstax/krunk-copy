from setuptools import setup

requires = ['docopt', 'bs4', 'python-dateutil', 'aiohttp']

setup(
    name='krunk-copy',
    version='0.0.4',
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
        'console_scripts': ['kcopy=krunk_copy:cli']
    },
    classifiers=[],
)
