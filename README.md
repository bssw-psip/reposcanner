# Reposcanner
A compact repository data mining toolkit

<img src="./logo.png" width="500">

## Dependencies

 - Python version >= 3.5
 - Pygit2 (for offline, clone-based analysis; tested with version 1.2.0)
 - Pygithub (for online, GitHub-based analysis; tested with version 1.47)
 
Install via pip:

```
pip install pygit2
pip install pygithub
```


## How To Use

Anatomy of invocation...
```
python reposcanner.py 
  --repo astropy/astropy     (a Github repository specified as {owner}/{name})
  --token 37d37acdce45568284399f6a849506c446fb26  (a GitHub personal acccess token (also supports --username and --password) instead)
  --outputDirectory ./  (where we want to store local output files)
  --localRepoDirectory ./temporary_repo_clone (if reposcanner needs to clone the repo, a path where it can store the clone)
```



