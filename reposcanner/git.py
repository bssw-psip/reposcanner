from enum import Enum,auto
import re
from abc import ABC, abstractmethod

import github as pygithub
import gitlab as pygitlab
import bitbucket as pybitbucket
import pygit2
        
class GitEntityFactory:
        def createRepositoryLocation(self,url,expectedPlatform=None,expectedHostType=None,expectedOwner=None,expectedRepositoryName=None):
                return RepositoryLocation(url=url,
                        expectedPlatform=expectedPlatform,
                        expectedHostType=expectedHostType,
                        expectedOwner=expectedOwner,
                        expectedRepositoryName=expectedRepositoryName)
                        
        def createVersionControlPlatformCredentials(self,username=None,password=None,token=None):
                return VersionControlPlatformCredentials(username=username,password=password,token=token)
                
        def createVCSAPISessionCompositeCreator(self):
                return VCSAPISessionCompositeCreator()
                
        def createGitHubAPISessionCreator(self):
                return GitHubAPISessionCreator()
                
        def createGitlabAPISessionCreator(self):
                return GitlabAPISessionCreator()

class VCSAPISessionCreator(ABC):
        """
        Abstract base class for a family of classes that talk 
        to version control system API libraries to establish
        sessions with those services.
        """
        @abstractmethod
        def canHandleRepository(self,repositoryLocation):
                """
                Returns True if the creator knows how to connect to a given repository,
                and False otherwise.
                
                repositoryLocation: A RepositoryLocation object.
                """
                pass
        
        @abstractmethod      
        def connect(self,repositoryLocation,credentials):
                """
                Attempts to establish a connection to a given repository using
                the credentials provided.
                
                repositoryLocation: A RepositoryLocation object.
                credentials: A VersionControlPlatformCredentials object.
                """
                pass
        
        
class VCSAPISessionCompositeCreator(VCSAPISessionCreator):
        """
        A Composite pattern class for VCSAPISessionCreators.
        """
        def __init__(self):
                self._children = []
                
        def addChild(self,child):
                self._children.append(child)
        
        def hasChild(self, child):
                return child in self._children

        def getNumberOfChildren(self):
                return len(self._children)

        def removeChild(self, child):
                self._children.remove(child)
        
        def canHandleRepository(self,repositoryLocation):
                for child in self._children:
                        if child.canHandleRepository(repositoryLocation):
                                return True
                return False

        def connect(self,repositoryLocation,credentials):
                for child in self._children:
                        if child.canHandleRepository(repositoryLocation):
                                return child.connect(repositoryLocation,credentials)
                        

class GitHubAPISessionCreator(VCSAPISessionCreator):
        
        def canHandleRepository(self,repositoryLocation):
                return repositoryLocation.getVersionControlPlatform() == RepositoryLocation.VersionControlPlatform.GITHUB
        
        def connect(repositoryLocation,credentials):
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
                        raise RuntimeError("GitHubAPISessionCreator received a VersionControlPlatformCredentials object \
                                with no username/password or token in it.")
                        
                repository = self.session.get_repo(repositoryLocation.getCanonicalName())
                return repository
                
class GitlabAPISessionCreator(VCSAPISessionCreator):
        
        def canHandleRepository(self,repositoryLocation):
                return repositoryLocation.getVersionControlPlatform() == RepositoryLocation.VersionControlPlatform.GITLAB
                
        def connect(self,repositoryLocation,credentials):
                if credentials.hasTokenAvailable():
                        session = gitlab.Gitlab(repositoryLocation.getRepositoryURL(), private_token=credentials.getToken())
                elif credentials.hasUsernameAndPasswordAvailable():
                        raise RuntimeError("The /session API endpoint used for username/password authentication \
                        has been removed from GitLab. Personal token authentication is the preferred authentication \
                        method.")
                else:
                        raise RuntimeError("GitlabAPISessionCreator received a VersionControlPlatformCredentials object \
                               with no username/password or token in it.")
                
                repository = session.projects.get(repositoryLocation.getCanonicalName())
                return repository
                
                
class BitbucketAPISessionCreator(VCSAPISessionCreator):
        
        def canHandleRepository(self,repositoryLocation):
                return repositoryLocation.getVersionControlPlatform() == RepositoryLocation.VersionControlPlatform.BITBUCKET
                
        def connect(self,repositoryLocation,credentials):
                #TODO: Need to figure out how to connect to the Bitbucket API.
                pass

class RepositoryLocation:
        """
        A convenience object that holds information about a repository
        on which we want to perform our analyses.
        """
        
        class VersionControlPlatform(Enum):
                GITHUB = auto()
                GITLAB = auto()
                BITBUCKET = auto()
                UNKNOWN = auto()
                
        class HostType(Enum):
                OFFICIAL = auto()
                SELFHOSTED = auto()
                UNKNOWN = auto()
        
        def _guessPlatformFromURL(self):
                """
                If the user does not explicitly state the expected platform (or type of platform)
                where the repository is located, we attempt to deduce this based on the URL. 
                """
                regexes = {
                        "GITHUB_OFFICIAL" : re.compile("github.com/.*?"),
                        "GITLAB_OFFICIAL" : re.compile("gitlab.com/.*?"),
                        "GITLAB_SELFHOSTED" : re.compile(".*?gitlab.*?"),
                        "BITBUCKET_OFFICIAL" : re.compile("bitbucket.org/.*?"),
                        "BITBUCKET_SELFHOSTED" : re.compile(".*?bitbucket.*?")
                }
                
                if regexes["GITHUB_OFFICIAL"].search(self._url):
                        self._platform = RepositoryLocation.VersionControlPlatform.GITHUB
                        self._hostType = RepositoryLocation.HostType.OFFICIAL
                elif regexes["GITLAB_OFFICIAL"].search(self._url):
                        self._platform = RepositoryLocation.VersionControlPlatform.GITLAB
                        self._hostType = RepositoryLocation.HostType.OFFICIAL
                elif regexes["GITLAB_SELFHOSTED"].search(self._url):
                        self._platform = RepositoryLocation.VersionControlPlatform.GITLAB
                        self._hostType = RepositoryLocation.HostType.SELFHOSTED
                elif regexes["BITBUCKET_OFFICIAL"].search(self._url):
                        self._platform = RepositoryLocation.VersionControlPlatform.BITBUCKET
                        self._hostType = RepositoryLocation.HostType.OFFICIAL
                elif regexes["BITBUCKET_SELFHOSTED"].search(self._url):
                        self._platform = RepositoryLocation.VersionControlPlatform.BITBUCKET
                        self._hostType = RepositoryLocation.HostType.SELFHOSTED
                else:
                        self._platform = RepositoryLocation.VersionControlPlatform.UNKNOWN
                        self._hostType = RepositoryLocation.HostType.UNKNOWN
                        
        def _guessOwnerAndRepositoryNameFromURL(self):
                """
                If the user does not explicitly state the expected owner and repository name, 
                we attempt to deduce these based on the URL. 
                """
                
                regexes = {
                        "GITHUB_OFFICIAL" : re.compile("^(?:(?:http|https)://)?github.com/([^/]+)/([^/]+)$"),
                        "GITLAB_OFFICIAL" : re.compile("^(?:(?:http|https)://)?gitlab.com/([^/]+)/([^/]+)$"),
                        "GITLAB_SELFHOSTED" : re.compile("^.*?gitlab.*?/([^/]+)/([^/]+)$"),
                        "BITBUCKET_OFFICIAL" : re.compile("^(?:(?:http|https)://)?bitbucket.org/([^/]+)/([^/]+)$"),
                        "BITBUCKET_SELFHOSTED" : re.compile("^.*?bitbucket.*?/([^/]+)/([^/]+)$"),
                        "UNKNOWN" : re.compile("^(?:(?:http|https)://)?.*?/([^/]+)/([^/]+)$")
                }
                
                if self._platform == RepositoryLocation.VersionControlPlatform.GITHUB:
                        regex = regexes["GITHUB_OFFICIAL"]
                elif self._platform == RepositoryLocation.VersionControlPlatform.GITLAB and self._hostType == RepositoryLocation.HostType.OFFICIAL:
                        regex = regexes["GITLAB_OFFICIAL"]
                elif self._platform == RepositoryLocation.VersionControlPlatform.GITLAB and self._hostType == RepositoryLocation.HostType.SELFHOSTED:
                        regex = regexes["GITLAB_SELFHOSTED"]
                elif self._platform == RepositoryLocation.VersionControlPlatform.BITBUCKET and self._hostType == RepositoryLocation.HostType.OFFICIAL:
                        regex = regexes["BITBUCKET_OFFICIAL"]
                elif self._platform == RepositoryLocation.VersionControlPlatform.BITBUCKET and self._hostType == RepositoryLocation.HostType.SELFHOSTED:
                        regex = regexes["BITBUCKET_SELFHOSTED"]
                elif self._platform == RepositoryLocation.VersionControlPlatform.UNKNOWN or self._hostType == RepositoryLocation.HostType.UNKNOWN:
                        regex = regexes["UNKNOWN"]
                else:
                        raise ValueError("In the RepositoryLocation class, _guessOwnerAndRepositoryLocationFromURL \
                        does not know how to parse this platform/hostType: {platform}/{hostType}. \
                        This is likely an implementation error.".format(platform=self._platform,hostType=self._hostType))
                
                match = regex.match(self._url)
                if match is None:
                        self._owner = None
                        self._repositoryName = None
                        
                else:
                        if len(match.group(1)) > 0:
                                self._owner = match.group(1)
                        else:
                                self._owner = None
                        if len(match.group(2)) > 0:
                                self._repositoryName = match.group(2)
                        else:
                                self._repositoryName = None
                
        
        
        def __init__(self,url,expectedPlatform=None,expectedHostType=None,expectedOwner=None,expectedRepositoryName=None):
                """
                Parameters:
                        url: The URL to the repository.
                        expectedPlatform (optional): 
                                        The expected platform where the repository is hosted. 
                                        By default, this is automatically detected, and does not
                                        need to be specified by the user.
                        expectedHostType (optional):
                                        If the user passes an expected platform, they should also
                                        pass an expected host type (e.g. hosted on an official site
                                        or self-hosted on a privately-owned server).
                        expectedOwner (optional):
                                        The organization or individual that is assumed to own the repository.
                                        For example, GitHub URLs are canonically written as
                                        https://github.com/<OWNER>/<REPOSITORYNAME>.
                                        Unless both <expectedOwner> and <expectedRepositoryName> are supplied,
                                        or they will both be overwritten by values estimated based on the URL.
                        expectedRepositoryName (optional):
                                        The name of the repository.
                                        For example, GitHub URLs are canonically written as
                                        https://github.com/<OWNER>/<REPOSITORYNAME>.
                                        Both <expectedOwner> and <expectedRepositoryName> should be supplied,
                                        or they will both be overwritten by values estimated based on the URL.
                                        
                """
                self._url = url
                if expectedPlatform is not None:
                        self._platform = expectedPlatform
                        if expectedHostType is not None:
                                self._hostType = expectedHostType
                        else:
                                self._hostType = RepositoryLocation.HostType.UNKNOWN
                else:
                        self._guessPlatformFromURL()
                if expectedOwner is not None and expectedRepositoryName is not None:
                        self._owner = expectedOwner
                        self._repositoryName = expectedRepositoryName
                else:
                        self._guessOwnerAndRepositoryNameFromURL()
                                
                        
                        
                
        def getURL(self):
                return self._url
                
        def getVersionControlPlatform(self):
                return self._platform
                
        def getVersionControlHostType(self):
                return self._hostType
                
        def getOwner(self):
                return self._owner
                
        def getRepositoryName(self):
                return self._repositoryName
                
        def getCanonicalName(self):
                return "{owner}/{repo}".format(owner=self._owner,repo=self._repositoryName)
                
        def isRecognizable(self):
                return (self._platform != RepositoryLocation.VersionControlPlatform.UNKNOWN and
                        self._hostType != RepositoryLocation.HostType.UNKNOWN and
                        self._owner != None and
                        self._repositoryName != None)
                

class VersionControlPlatformCredentials:
        """
        Holds credentials for logging in to GitHub, which can be done either by supplying a token
        or a username and password. If the client supplies a username and password, we will use those.
        Alternatively, if the client supplies a token, then we will use that instead. If all of the above,
        then the username and password should take precedence.
        """
        def __init__(self,username=None,password=None,token=None):
                """
                Parameters:
                        username (@input): A string containing the client's handle.
                        password (@input): A string containing the client's password.
                        token (@input): A string containing a token associated with the user's account.
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
  
  
