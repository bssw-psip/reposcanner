# Reposcanner

<img src="./images/logo.png" width="500">

[![Build Passing](https://github.com/bssw-psip/reposcanner/actions/workflows/python-package.yml/badge.svg)](https://github.com/bssw-psip/reposcanner/actions/workflows/python-package.yml)

Reposcanner provides a highly modular, extensible framework for defining routines for mining data from software repositories and performing analyses on that data to yield valuable insights on team behaviors. Reposcanner provides a number of attractive features not normally seen in repository mining research codes, such as seamless support for different version control platforms like GitHub, Gitlab, and Bitbucket, smart parsing of URLs, intelligent credential management capabilities, and a comprehensive test suite. 


<img src="./images/highLevelArchitecture.png" height="417">

The diagram above illustrates the overall architecture of the Reposcanner toolkit. Data collection operations are represented as task objects which are consumed by mining routines. The resulting data is held in a communal data store which can be leveraged by downstream analyses responsible for graphs, summaries, and other artifacts.

## How to Install

First, clone the repository from GitHub:

```
git clone https://github.com/bssw-psip/reposcanner.git
```

Then install Reposcanner and run the test suite:

```
cd reposcanner
python3 -m venv ../repo-env # create a new virtual environment
. ../repo-env/bin/activate  # activate the new virtual env
pip install -e .            # create editable install
tox                         # run tests
```

If all tests pass, the installation was successful, and you are ready to go!


# How to Run

## Setup input files

We'll run the example scan specified inside `tutorial/inputs` directory.

1. First, add your github token to the `token:` line in `tutorial/inputs/credentials.yml`

2. Run the reposcanner tool using:

```
reposcanner --credentials tutorial/inputs/credentials.yml --config tutorial/inputs/config.yml --repositories tutorial/inputs/repositories.yml --workspaceDirectory tutorial/workspace --outputDirectory tutorial/outputs --notebookOutputPath tutorial/outputs
```

3. examine the output files written to `tutorial/outputs`


# How to extend functionality

1. Create a new source file, `src/reposcanner/<routine.py>`, including a class
   based on the `ContributorAccountListRoutine`.  See `stars.py` as an
   example of the kind of modifications required.

2. Add the new class name (for example `- StarGazersRoutine`) to the end of `config.yml`.

3. Run the test scan and inspect output to ensure your scan worked as intended.

