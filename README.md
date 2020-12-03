# Protocol sentiments

## Requirements

- python 3.8
- pre-commit
- poetry > 1.0.0

## Setting up

```powershell
make setup    # this will create the virtual environment in the repo with poetry
```

## Reading the data

In order to read the data you can call:

```powershell
python protocols/import_data.py    #this extracts the data from the locally cloned repo
```

You need to change the relative path to the repo you want to parse, the code only read the markdown files, gets the first code committer per file, the data of the commit and extracts the text from html, extracted from markdown.

The new dataset is saved in a **data** folder.