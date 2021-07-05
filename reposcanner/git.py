from enum import Enum,auto
import re, urllib3
from abc import ABC, abstractmethod

import github as pygithub
import gitlab as pygitlab
import bitbucket as pybitbucket
import pygit2
from atlassian.bitbucket.cloud import Cloud
        
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
        
        def connect(self,repositoryLocation,credentials):
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
                        raise RuntimeError("GitHubAPISessionCreator received a VersionControlPlatformCredentials object"
                                "with no username/password or token in it.")
                        
                repository = session.get_repo(repositoryLocation.getCanonicalName())
                return repository
                
class GitlabAPISessionCreator(VCSAPISessionCreator):
        
        def canHandleRepository(self,repositoryLocation):
                return repositoryLocation.getVersionControlPlatform() == RepositoryLocation.VersionControlPlatform.GITLAB
                
        def connect(self,repositoryLocation,credentials):
                if credentials.hasTokenAvailable():
                        session = gitlab.Gitlab(repositoryLocation.getRepositoryURL(), private_token=credentials.getToken())
                elif credentials.hasUsernameAndPasswordAvailable():
                        raise RuntimeError("The /session API endpoint used for username/password authentication"
                        "has been removed from GitLab. Personal token authentication is the preferred authentication "
                        "method.")
                else:
                        raise RuntimeError("GitlabAPISessionCreator received a VersionControlPlatformCredentials object"
                               "with no username/password or token in it.")
                
                repository = session.projects.get(repositoryLocation.getCanonicalName())
                return repository
                
                
class BitbucketAPISessionCreator(VCSAPISessionCreator):
        
        def canHandleRepository(self,repositoryLocation):
                return repositoryLocation.getVersionControlPlatform() == RepositoryLocation.VersionControlPlatform.BITBUCKET
                
        def connect(self,repositoryLocation,credentials):
                if credentials.hasTokenAvailable():
											raise RuntimeError("bitbucket cloud api does not have token login")
								else: credentials.hasUsernameAndPasswordAvailable():
											try: bb = Cloud(url = 'https://api.bitbucket.org', username = credentials.getUsername(),\
											password = credentials.getPassword(), cloud = True)
											execpt: raise RuntimeError("Bitbucket cloud api needs username and password")
#this is going to assume the workspace name is the same as username. Will change this if needed
								repository = bb.workspace.get(credentials.getUsername()).repositories.get(repositoryLocation.getCanonicalName())
								return repository

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
        Holds credentials for logging in to a version control platform, 
        which can be done either by supplying a token or a username and password. 
        If the client supplies a username and password, we will use those.
        Alternatively, if the client supplies a token, then we will use that instead. 
        If all of the above, then the username and password should take precedence.
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
                
class CredentialKeychain:
        """
        A keychain holds a collection of credentials 
        and can provide credentials on demand.
        Request objects look up the credentials 
        they need from a keychain during construction.
        """
        
        def __init__(self,credentialsDictionary):
                """
                credentialsDictionary: A dictionary containing credentials information.
                """
                self._credentials = {}
                
                if type(credentialsDictionary) != dict:
                        raise TypeError("CredentialKeychain constructor expected to receive \
                        a dictionary object, but got a {wrongType} instead!".format(
                        wrongType=type(credentialsDictionary)))
                        
                
                def safeAccess(dictionary,key):
                        """A convenience function for error-free access to a dictionary"""
                        if key in dictionary:
                                return dictionary[key]
                        else:
                                return None
                
                for entryName in credentialsDictionary:
                        entry = credentialsDictionary[entryName]
                        url = safeAccess(entry,"url")
                        username = safeAccess(entry,"username")
                        password = safeAccess(entry,"password")
                        token = safeAccess(entry,"token")
                        if url is None:
                                print("Reposcanner: Warning, the entry {entryName} in \
                                the credentials file is missing a URL. Skipping.".format(
                                entryName=entryName))
                                continue
                        try:
                               credentialsObject = VersionControlPlatformCredentials(username,password,token)
                        except ValueError as error:
                                print("Reposcanner: Warning, the entry {entryName} in \
                                the credentials file is missing a username\password \
                                combo, a token, or both. Skipping.".format(
                                entryName=entryName))
                                continue
                        self._credentials[url] = credentialsObject
                        
        def __len__(self):
                return len(self._credentials)
                
        
        def lookup(self,repositoryLocation):
                """
                Fetches a key from a keychain based on a RepositoryLocation's URL.
                If the URL matches more than one entry (e.g. a platform-wide entry
                vs. a repository-specific entry), the keychain returns the credentials
                for the longest, closest match. 
                
                repositoryLocation: A RepositoryLocation instance.
                """
                repositoryURL = repositoryLocation.getURL()
                matches = []
                for url in self._credentials:
                        #Substring match
                        if url in repositoryURL:
                                matches.append(url)
                if len(matches) == 0:
                        return None
                else:
                        longestMatch = max(matches)
                        return self._credentials[longestMatch]
                        
                        


  
  
