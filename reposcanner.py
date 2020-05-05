import argparse
from abc import ABC, abstractmethod
#import matplotlib.pyplot as plt
#import seaborn as sns
import urllib3
import os
import time, datetime
import statistics
import csv

try:
        import github as pygithub #For working with the GitHub API.
        pygithubAvailable = True
except ImportError as error:
        print("\n***********\nREPOSCANNER WARNING: Failed to import pygithub (see message below). GitHub-based analyses are disabled.\n{message}\n***********\n".format(message=str(error)))
        pygithubAvailable = False

try:
        import pygit2 #For working with local clones of repositories.
        pygitAvailable = True
except ImportError as error:
        print("\n***********\nREPOSCANNER WARNING: Failed to import pygit2 (see message below). Clone-based analyses are disabled.\n{message}\n***********\n".format(message=str(error)))
        pygitAvailable = False

class RepositoryName:
        """
        A convenience value-object that holds the owner and name of a repository on which we want to perform our analyses.
        """
        
        def __init__(self,combinedString):
                """
                Parameters:
                        combinedString: A string of the form '<owner>/<repo>'.
                """
                if not isinstance(combinedString, str):
                        raise TypeError("RepositoryAnalysisRoutine expects <combinedString> to be a string.")
                elements = combinedString.split('/')
                if len(elements) != 2:
                        raise ValueError("RepositoryName constructor failed to parse <combinedString>, expected '<owner>/<repo>' format.")
                else:
                        self._owner = elements[0]   
                        self._repositoryName = elements[1]
        
        def getOwner(self):
                return self._owner
                
        def getRepositoryName(self):
                return self._repositoryName
        
        def getCanonicalName(self):
                """
                Provides the name of the repository in the canonical format (i.e. '<owner>/<repo>')
                """
                return "{owner}/{repositoryName}".format(owner=self._owner,repositoryName=self._repositoryName)
                
        def getURL(self):
                """
                Construct a GitHub URL for the repository.
                """
                return "https://github.com/{owner}/{repositoryName}".format(owner=self._owner,repositoryName=self._repositoryName)
                

class GitHubCredentials:
        """
        Holds credentials for logging in to GitHub, which can be done either by supplying a token
        or a username and password. If the client supplies a username and password, we will use those.
        Alternatively, if the client supplies a token, then we will use that instead. If all of the above,
        then the username and password should take precedence.
        """
        def __init__(self,username=None,password=None,token=None):
                """
                Parameters:
                        username (@input): A string containing the client's GitHub handle.
                        password (@input): A string containing the client's GitHub password.
                        token (@input): A string containing a token associated with the user's GitHub account.
                """
                self._username = username
                self._password = password
                self._token = token
                if (self._username and not self._password) or (not self._username and self._password):
                        raise ValueError("Client supplied a username without a password, or a password without a username.")
                if (self._username is None and self._password is None and self._token == None):
                        raise ValueError("Client did not supply a username/password or token. We need one of these in order to proceed!")
        
        def hasUsernameAndPasswordAvailable(self):
                return self._username is not None and self._password is not None
                
        def hasTokenAvailable(self):
                return self._token is not None
                
        def getUsername(self):
                return self._username
        
        def getPassword(self):
                return self._password
                
        def getToken(self):
                return self._token
  
  
class RepositoryAnalysisRoutine(ABC):
        """The abstract base class for all repository analysis routines. Methods cover
        the execution of analyses, rendering, and exporting of data."""
        
        @abstractmethod
        def execute(self):
                """
                Contains the code for interacting with the GitHub repository via PyGitHub. 
                Whatever data this method returns will be passed to the render and export methods.
                """
                pass
        
        @abstractmethod        
        def render(self,data):
                """
                Contains the code for rendering data via Matplotlib.
                
                Parameters:
                        data (@input): The data generated by the execute() method.
                """
                pass
         
        @abstractmethod       
        def export(self,data):
                """
                Contains the code for exporting data to a file.
                
                Parameters:
                        data (@input): The data generated by the execute() method.
                """
                pass
                
        def run(self):
                """
                Encodes the workflow of a RepositoryAnalysisRoutine object. The client only needs
                to run this method in order to get results. 
                """
                data = self.execute()
                self.render(data)
                self.export(data)              
 
 
class OfflineRepositoryAnalysisRoutine(RepositoryAnalysisRoutine):
        """
        Class that encapsulates the stages of a PyGit2-based analysis procedure operating on a clone of a repository.
        """
        def __init__(self,repositoryName,localRepoDirectory,outputDirectory):
                if not isinstance(localRepoDirectory, str):
                        raise TypeError("OfflineRepositoryAnalysisRoutine expects <localRepoDirectory> to be a string.")
                if not isinstance(repositoryName, RepositoryName):
                        raise TypeError("OfflineRepositoryAnalysisRoutine expects <repositoryName> to be a RepositoryName object.")
                
                self.repository = self._cloneRepositoryIfMissing(repositoryName,localRepoDirectory)
                self.repositoryName = repositoryName
                self.outputDirectory = outputDirectory
                
        def _cloneRepositoryIfMissing(self,repositoryName,localRepoDirectory):
                if not os.path.exists(localRepoDirectory):
                        clone = pygit2.clone_repository(repositoryName.getURL(), localRepoDirectory)
                        return clone
                else:
                        clone = pygit2.Repository(localRepoDirectory)
                        return clone      
                      
class OnlineRepositoryAnalysisRoutine(RepositoryAnalysisRoutine):
        """
        Class that encapsulates the stages of an PyGitHub-based analysis procedure operating on the GitHub API.
        """
        def __init__(self,credentials,repositoryName,outputDirectory):
                
                if not isinstance(credentials, GitHubCredentials):
                        raise TypeError("OnlineRepositoryAnalysisRoutine expects <credentials> to be provided as a GitHubCredentials object.")
                if not isinstance(repositoryName, RepositoryName):
                        raise TypeError("OnlineRepositoryAnalysisRoutine expects <repositoryName> to be a RepositoryName object.")     
                self.session = self._connect(credentials)
                self.repository = self._lookupRepository(repositoryName)
                self.repositoryName = repositoryName
                self.outputDirectory = outputDirectory
                

        def _connect(self,credentials):
                """Establishes a session to the GitHub API so we can get data on the requested repository."""
                status_forcelist = (500, 502, 504) #These status codes are caused by random GitHub errors which should trigger a retry.
                totalAllowedRetries = 3
                allowedReadErrorRetries = 3
                allowedConnectionErrorRetries = 3
                retryHandler = urllib3.Retry(total=totalAllowedRetries, 
                        read=allowedReadErrorRetries, 
                        connect=allowedConnectionErrorRetries, 
                        status_forcelist=status_forcelist)
                
                if credentials.hasUsernameAndPasswordAvailable():
                        session = pygithub.Github(credentials.getUsername(),credentials.getPassword(),retry=retryHandler) 
                elif credentials.hasTokenAvailable():
                        session = pygithub.Github(credentials.getToken(),retry=retryHandler)
                else:
                        raise RuntimeError("RepositoryAnalysisRoutine received a GitHubCredentials object with no username/password or token in it.")
                return session
                        
                        
        def _lookupRepository(self,repositoryName):
                return self.session.get_repo(repositoryName.getCanonicalName())
                

class ContributorAccountListRoutine(OnlineRepositoryAnalysisRoutine):
        """
        Contact the GitHub API, and get the account information of everyone who has ever contributed to the repository.
        """

        def __init__(self,credentials,repositoryName,outputDirectory):
                super().__init__(repositoryName=repositoryName,credentials=credentials,outputDirectory=outputDirectory)
                
        def execute(self):
                contributors = [contributor for contributor in self.repository.get_contributors()]
                return contributors
                
        def render(self,data):
                pass
        def export(self,data):
                contributors = data
                today = datetime.datetime.now()
                
                with open('{outputDirectory}/{repoName}_contributorAccounts.csv'.format(
                        outputDirectory=self.outputDirectory,repoName=self.repositoryName.getRepositoryName()),'w', newline='\n') as contributorAccountsFile:
                        
                        contributionWriter = csv.writer(contributorAccountsFile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        contributionWriter.writerow(["Date/Time of Analysis", "{dateOfAnalysis}".format(dateOfAnalysis=str(today))])
                        contributionWriter.writerow(["Repository", "{canonicalName}".format(canonicalName=self.repositoryName.getCanonicalName())])
                        
                        
                        contributionWriter.writerow([
                                "Login Name",
                                "Actual Name",
                                "Email",
                                "URL",
                        ])
                        
                        for contributor in contributors:
                                contributionWriter.writerow([contributor.login,contributor.name,contributor.email,contributor.url])                       
                        
                        
                        

class ContributionPeriodRoutine(OfflineRepositoryAnalysisRoutine):
        """
        Calculates the number of mount of contri contribution periods of different contributors 
        """
        def __init__(self,repositoryName,localRepoDirectory,outputDirectory):
                super().__init__(repositoryName=repositoryName,localRepoDirectory=localRepoDirectory,outputDirectory=outputDirectory)
        
        def execute(self):
                contributors = []
                numberOfCommitsByContributor = {}
                timestampsByContributor = {}        
                
                for commit in self.repository.walk(self.repository.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
                        if commit.author.name not in contributors:
                                contributors.append(commit.author.name)
                        
                        if commit.author.name not in numberOfCommitsByContributor:
                                numberOfCommitsByContributor[commit.author.name] = 1
                        else:
                                numberOfCommitsByContributor[commit.author.name] += 1
                        
                        timeOfCommit = commit.commit_time
                        
                        if commit.author.name not in timestampsByContributor:
                                timestampsByContributor[commit.author.name] = (timeOfCommit,timeOfCommit)
                        else:
                                firstCommit,latestCommit = timestampsByContributor[commit.author.name]
                                if timeOfCommit < firstCommit:
                                        timestampsByContributor[commit.author.name] = (timeOfCommit,latestCommit)
                                if timeOfCommit > latestCommit:
                                        timestampsByContributor[commit.author.name] = (firstCommit,timeOfCommit)
                        
                return contributors,numberOfCommitsByContributor,timestampsByContributor
                
        def render(self,data):
                pass

        def export(self,data):
                contributors,numberOfCommitsByContributor,timestampsByContributor = data
                
                today = datetime.datetime.now()
                
                with open('{outputDirectory}/{repoName}_contributionPeriods.csv'.format(
                        outputDirectory=self.outputDirectory,repoName=self.repositoryName.getRepositoryName()),'w', newline='\n') as contributionPeriodsFile:
                        
                        contributionWriter = csv.writer(contributionPeriodsFile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        
                        contributionWriter.writerow(["Date/Time of Analysis", "{dateOfAnalysis}".format(dateOfAnalysis=str(today))])
                        contributionWriter.writerow(["Repository", "{canonicalName}".format(canonicalName=self.repositoryName.getCanonicalName())])
                        
                        contributionWriter.writerow([
                                "Contributor Name",
                                "Number of Commits By Contributor",
                                "Timestamp of First Commit",
                                "Timestamp of Last Commit",
                                "Length of Contribution Period (In Days)",
                                "Has Made a Commit in the Past 365 Days"
                        ])
                        contributionPeriodsInDays = { contributor : ((timestampsByContributor[contributor][1] - timestampsByContributor[contributor][0]) / 60 / 60 / 24) for contributor in timestampsByContributor }
                        for contributor in contributors:
                                contributorName = contributor
                                numberOfCommits = numberOfCommitsByContributor[contributor]
                                firstCommitTimestamp,lastCommitTimestamp = timestampsByContributor[contributor]
                                contributionPeriod = numberOfCommitsByContributor[contributor]
                                
                                activeInPastYear = ((today.timestamp() - lastCommitTimestamp) / 60 / 60 / 24) <= 365
                                
                                contributionWriter.writerow([contributorName,numberOfCommits,firstCommitTimestamp,lastCommitTimestamp,contributionPeriod,activeInPastYear])
                                
                                



def scannerMain(args):
        """
        The master routine for Reposcanner.
        """
        global pygitAvailable, pygithubAvailable
        if args.enableLocalAnalyses is True and not pygitAvailable:
                args.enableLocalAnalyses = False
        if args.enableOnlineAnalyses is True and not pygithubAvailable:
                args.enableOnlineAnalyses = False
        
        credentials = GitHubCredentials(username=args.username,password=args.password,token=args.token)
        repositoryName = RepositoryName(combinedString=args.repo)
        
        if not os.path.exists(args.outputDirectory):
                raise OSError("Reposcanner couldn't find the specified output directory. Shutting down as a precaution.")
        
        
        contributionPeriodRoutine = ContributionPeriodRoutine(repositoryName=repositoryName,localRepoDirectory=args.localRepoDirectory,outputDirectory=args.outputDirectory)
        contributionPeriodRoutine.run()
        
        accountListRoutine = ContributorAccountListRoutine(repositoryName=repositoryName,credentials=credentials,outputDirectory=args.outputDirectory)
        accountListRoutine.run()

if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='The IDEAS-ECP PSIP Team Repository Scanner. Note: To use this tool for online PyGitHub-based analyses, you must supply either a username and password or an access token to communicate with the GitHub API.')
        parser.add_argument('--repo', action='store', type=str, help='The canonical name of the GitHub repository we want to study (expected form: owner/repoName).')
        parser.add_argument('--username',action='store',type=str,default=None,help='The username of the account used to talk to the GitHub API.')
        parser.add_argument('--password',action='store',type=str,default=None,help='The password of the account used to talk to the GitHub API.')
        parser.add_argument('--token',action='store',type=str,default=None,help='The token of the account used to talk to the GitHub API.')
        parser.add_argument('--outputDirectory',action='store',type=str,default='./',help='The path where we should output files. By default this is done in the directory from which this script is run.')
        parser.add_argument('--enableOnlineAnalyses', help='Set this flag to allow the reposcanner to perform analyses which require the tool to talk to the GitHub API. This clone will be cleaned up at termination.')
        parser.add_argument('--enableLocalAnalyses', help='Set this flag to allow the reposcanner to perform analyses which require the tool to make a clone of the repository. This clone will be removed at termination.')
        parser.add_argument('--localRepoDirectory',action='store',type=str,default='./temporary_repo_clone',help='If you want reposcanner to perform certain analyses that require a local clone of the repository, then it must have a location where it can clone the repository. By default this is done in the directory from which this script is run.')
        args = parser.parse_args()
        scannerMain(args)
        
        