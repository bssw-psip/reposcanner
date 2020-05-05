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
  
  
