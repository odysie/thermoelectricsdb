# thermoelectricsdatabase

Tools for auto-generating a thermoelectric-materials database.

## Installation

To install the latest public ChemDataExtractor version (v2.0.2.):
```
pip install chemdataextractor2==2.0.2
```

Download the necessary data files (machine learning models, dictionaries, etc.):
```
cde data download
```

To install the version of ChemDataExtractor adapted for use on the thermoelectric-materials domain, navigate to ./chemdataextractor_thermoelectrics/chemdataextractor/dist/,  untar the .tar file, and from the resulting folder
```
pip install -r requirements.txt
pip setup.py install
```

## Usage

The example_run.module shows how to extract a small database for a given property, from the articles in the test_articles folder.
```
python example_run.py
```

After the database is extracted, it should be cleaned and formatted. The data-cleaning code is provided in `data_cleaning.ipynb`. Code for aggregating a database with all five properties is found in `data_aggregation.ipynb`

## Citation

```

```