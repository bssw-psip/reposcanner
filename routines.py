from abc import ABC, abstractmethod
import urllib3
import os
from git import *

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
        def __init__(self,repositoryName,localRepoDirectory,outputDirectory,**kws):
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
        def __init__(self,credentials,repositoryName,outputDirectory,**kws):
                
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
