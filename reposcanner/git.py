from enum import Enum,auto
import re

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
        
        
#TODO: APISessionFactory, APISession, etc. to decouple routines from connecting to version control platforms.
        
class GitEntityFactory:
        def createRepositoryLocation(self,url,expectedPlatform=None,expectedHostType=None,expectedOwner=None,expectedRepositoryName=None):
                return RepositoryLocation(url=url,
                        expectedPlatform=expectedPlatform,
                        expectedHostType=expectedHostType,
                        expectedOwner=expectedOwner,
                        expectedRepositoryName=expectedRepositoryName)
                        
        def createVersionControlPlatformCredentials(self,username=None,password=None,token=None):
                return VersionControlPlatformCredentials(username=username,password=password,token=token)


class RepositoryLocation:
        """
        A convenience value-object that holds information about a repository
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
  
  
