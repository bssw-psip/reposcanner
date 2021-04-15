# Reposcanner

<img src="./images/logo.png" width="500">

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
python setup.py install
python -m pytest
```

If all tests pass, the installation was successful, and you are ready to go!


# How to Run

TBD! 


