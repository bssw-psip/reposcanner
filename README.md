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

Reposcanner will attempt to run its battery of analysis routines, conveniently encapsulated in RepositoryAnalysisRoutine objects.

## Example: ContributionPeriodRoutine

### How it works

- First, ContributionPeriodRoutine makes a clone of the repository for offline analysis. This is done to avoid spamming the GitHub API with thousands of calls (which can happen when we do deep queries on commit logs).
- Next, it walks the commit logs and creates a record of each unique contributor to the repository, the number of commits they have made, and the timestamps of their first and last commit.
- It records this information in a CSV file.

### Example output (for Astropy/Astropy)

```
Date/Time of Analysis,2020-04-28 13:01:09.946450
Repository,astropy/astropy
Contributor Name,Number of Commits By Contributor,Timestamp of First Commit,Timestamp of Last Commit,Length of Contribution Period (In Days),Has Made a Commit in the Past 365 Days
Brigitta Sipőcz,94,1574841036,1588044597,94,True
Lauren Glattly,191,1552503739,1588010582,191,True
lglattly,17,1560964729,1588008347,17,True
Tom Aldcroft,2404,1318606958,1587979803,2404,True
Marten van Kerkwijk,1753,1369859762,1587812519,1753,True
Larry Bradley,655,1382454799,1587760827,655,True
Erik Tollerud,3483,1311627702,1587755956,3483,True
Tom,8,1561147655,1587753296,8,True
Julien Woillez,129,1345056360,1587738986,129,True
Zlatan Vasović,1,1587756113,1587756113,1,True
Simon Conseil,605,1411419767,1587752066,605,True
ndl303,4,1587175325,1587595611,4,True
Nadia Dencheva,668,1366505858,1587732225,668,True
Ed Slavich,13,1582051661,1587679131,13,True
Pey Lian Lim,686,1358284746,1587687664,686,True
P. L. Lim,430,1432650808,1587678148,430,True
James Davies,30,1528230190,1587655744,30,True
Clara Brasseur,7,1540576518,1587602803,7,True
perrygreenfield,69,1418335074,1587662838,69,True
Mihai Cara,66,1407146268,1587658425,66,True
Brigitta Sipocz,1435,1393724928,1587619389,1435,True
David Stansby,25,1516122129,1584706665,25,True
Stuart Mumford,347,1382807106,1587544889,347,True
broulston,26,1554133489,1586962136,26,True
Jerry Ma,3,1463223541,1587477669,3,True
Miguel de Val-Borro,36,1377441763,1587418443,36,True
[...]
```

**Note**: There are some caveats to doing offline analysis in this way. Because we're matching commits with names written on the commit log rather than actual GitHub accounts, there can be some artifacts and anomalous results that will need to be cleaned up, such as these:

```
(I highly suspect that there is only one Mr. Bakanov, rather than two brothers with slightly different names)
Aleksandr Bakanov,1,1533394762,1533394762,1,False  
Alexander Bakanov,6,1502289531,1532504743,6,False

(These could be the same Pauline, but the second Pauline is missing a last name, so it's hard to tell unless we can tie these to the actual GitHub accounts)
Pauline Barmby,6,1424447192,1434546575,6,False
Pauline,4,1429620027,1429620761,4,False

(who is "--system"?! "unknown"?!)
--system,4,1530392168,1541846540,4,False
unknown,3,1520060118,1520060119,3,False
```



