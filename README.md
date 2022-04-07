# thermoelectricsdatabase

Tools for auto-generating a thermoelectric-materials database.

## Installation

Please first install the public ChemDataExtractor version (v2.0.2.):
```
pip install chemdataextractor2==2.0.2
```

Download the necessary data files (machine learning models, dictionaries, etc.):
```
cde data download
```


## Usage

To extract raw data from text, you need to provide the root of the paper folder, output root to data record folder, start and end index of papers, and the file name to be saved.

For example, extract the first paper of `test/` and save to `save/` as `raw_data.json`:
```
python extract.py --input_dir test/ --output_dir save/ --start 0 --end 1 --save_name raw_data
```

After the raw data is extracted, it needs to be cleaned and converted into a standard format. We provide the data cleaning code in `dataclean.ipynb`. The final data format can be `.json`, `.csv` or `.db`.

## Citation

```

```