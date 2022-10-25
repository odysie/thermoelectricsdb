# thermoelectricsdatabase

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](https://github.com/odysie/thermoelectricsdb/blob/main/LICENSE)

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

## Acknowledgements

This project was financially supported by the <u>Science and Technology Facilities Council (STFC)</u>, the <u>Royal Academy of Engineering</u> (RCSRF1819\7\10) and the Engineering and Physical Sciences Research Council (EPSRC) for PhD funding (EP/R513180/1 (2020–2021) and EP/T517847/1 (2021–2024)). The Argonne Leadership Computing Facility, which is a <u>DOE Office of Science Facility</u>, is also acknowledged for use of its research resources, under contract No. DEAC02-06CH11357.

## Citation

```
 @article{sierepeklis_cole_2022,
 title={A thermoelectric materials database auto-generated from the scientific literature using chemdataextractor},
 journal={Nature News},
 publisher={Nature Publishing Group},
 author={Sierepeklis, Odysseas and Cole, Jacqueline M.},
 year={2022},
 month={Oct}} 
}
```
[![DOI](https://zenodo.org/badge/DOI/10.1038/s41597-022-01752-1.svg)](https://doi.org/10.1038/s41597-022-01752-1)