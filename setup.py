import setuptools

###
# Test the package live on anaconda prompt with:
#   cd /tribus/
#   python setup.py develop
#   pip install  -e ./
#   cd ../test data
# tribus classify -i input_data/ -l gate_logic_1.xlsx -o test_results
#
#
###

requires = [
    'numpy>=1.18.1',
    'matplotlib>=3.1.2',
    'networkx>=2.4',
    'scipy>=1.4.1',
    'scikit-image==0.16.2',
    'scikit-learn>=0.21.1',
    'pandas',
    'openpyxl',
]

VERSION = '0.0.1'
DESCRIPTION = 'Cell type based analysis of multiplexed imaging data'
LONG_DESCRIPTION='''
Tribus is a lightweight package to help analysis of multiplexed imaging data, such as cyclic immunofluorescence imaging (CyCIF). Its core functionality lies on automatic cell type assignment of large datasets via hiarchical categorization based on user-given prior knowledge from the user.
'''
AUTHOR = 'Julia Casado, Angela Szabo, Miikka Kilkkila'
AUTHOR_EMAIL = 'julia.casado@helsinki.fi'
HOMEPAGE = 'https://github.com/farkkilab/tribus'

setuptools.setup(
    name='tribus',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url=HOMEPAGE,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'tribus = tribus.tribus:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
    ],
    python_requires='>=3.6',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
)