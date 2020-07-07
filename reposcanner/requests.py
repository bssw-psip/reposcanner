import datetime
import reposcanner.git as gitEntities
import os.path
from abc import ABC, abstractmethod


class BaseRequestModel:
        """
        The base class for all request models. The frontend is responsible for phrasing their requests in the
        form of a request model which routines understand.
        """

        def __init__(self,repositoryURL,outputDirectory):
                """
                parameters:
                        repositoryURL (@input): A URL to a version control
                                repository hosted online.
                
                        outputDirectory (@input): The directory where files generated
                                by the routine should be stored.
                
                """
                self._errors = []
                factory = gitEntities.GitEntityFactory()
                self._repositoryLocation = None
                try:
                        self._repositoryLocation = factory.createRepositoryLocation(url=repositoryURL)
                        if not self._repositoryLocation.isRecognizable():
                                self.addError("Reposcanner failed properly parse this URL: {url}. This may be \
                                because it does not know the platform or cannot extract an owner/repo from the \
                                address".format(url=repositoryURL))
                except Exception as exception:
                        self.addError("Encountered an unexpected exception \
                        while constructing a RepositoryLocation \
                        from the input URL {url}: {exception}".format(url=repositoryURL,exception=exception))
                
                try:
                        self._outputDirectory = outputDirectory
                        if not os.path.isdir(self._outputDirectory) or not os.path.exists(self._outputDirectory):
                                self.addError("The output directory {outputDirectory} either does not exist or \
                                is not a valid directory.".format(outputDirectory=self._outputDirectory))
                except Exception as exception:
                        self.addError("Encountered an unexpected exception \
                        while parsing output directory \
                        {outputDirectory}: {exception}".format(outputDirectory=self._outputDirectory,
                        exception=exception))
                
                
        def getRepositoryLocation(self):
                return self._repositoryLocation
                
        def getOutputDirectory(self):
                return self._outputDirectory

        def addError(self, message):
                self._errors.append(message)

        def hasErrors(self):
                return len(self._errors) > 0

        def getErrors(self):
                return self._errors
                

class OnlineRoutineRequest(BaseRequestModel):
        """
        The base class for requests to routines that use an online API to compute results. 
        Request classes for OnlineRepositoryAnalysisRoutine should inherit from this class.
        """
        def __init__(self,repositoryURL,outputDirectory,username=None,password=None,token=None):
                """
                Additional Parameters:
                
                username (@input): A string containing the client's handle.
                
                password (@input): A string containing the client's password.
                
                token (@input): A string containing a token associated with the user's account.
                """
                super().__init__(repositoryURL,outputDirectory)
                
                self._credentials = None
                factory = gitEntities.GitEntityFactory()
                try:
                        self._credentials = factory.createVersionControlPlatformCredentials(
                                username=username,
                                password=password,
                                token=token)
                except Exception as exception:
                        self.addError("Encountered an unexpected exception \
                        while constructing credentials object: {exception}".format(exception=exception))
                        
        def getCredentials(self):
                return self._credentials
                
class OfflineRoutineRequest(BaseRequestModel):
        """
        The base class for requests to routines that operate on an offline clone to compute results. 
        Request classes for OfflineRepositoryAnalysisRoutine should inherit from this class.
        """
        def __init__(self,repositoryURL,outputDirectory,workspaceDirectory):
                """
                Additional Parameters:
                
                workspaceDirectory (@input): The directory under which Reposcanner 
                        should create a clone of the input repository.
                """
                super().__init__(repositoryURL,outputDirectory)
                try:
                        self._workspaceDirectory = workspaceDirectory
                        if not os.path.isdir(self._workspaceDirectory) or not os.path.exists(self._workspaceDirectory):
                                self.addError("The workspace directory {workspaceDirectory} either does not exist or \
                                is not a valid directory.".format(outputDirectory=self._workspaceDirectory))
                except Exception as exception:
                        self.addError("Encountered an unexpected exception \
                        while parsing workspace directory \
                        {workspaceDirectory}: {exception}".format(workspaceDirectory=self._workspaceDirectory,
                        exception=exception))
                        
        def getCloneDirectory(self):
                return "{workspace}/{repoName}".format(workspace=self._workspaceDirectory,repoName=self.getRepositoryLocation().getRepositoryName())
                
        def getWorkspaceDirectory(self):
                return self._workspaceDirectory
                         
                        