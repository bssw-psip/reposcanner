import datetime
import reposcanner.git as gitEntities
import os
from pathlib import Path
from abc import ABC, abstractmethod

class BaseRequestModel:
        """
        The base class for all request models. The frontend is responsible for phrasing their requests in the
        form of a request model which routines/analyses understand.
        """
        def __init__(self):
                self._errors = []
        
        def addError(self, message):
                self._errors.append(message)

        def hasErrors(self):
                return len(self._errors) > 0

        def getErrors(self):
                return self._errors
                
        @classmethod
        def isRoutineRequestType(cls):
                return False
        
        @classmethod      
        def isAnalysisRequestType(cls):
                return False     


class AnalysisRequestModel(BaseRequestModel):
        
        @classmethod      
        def isAnalysisRequestType(cls):
                return True
                
        def __init__(self,outputDirectory="./"):
                super().__init__()
                self._data = []
                try:
                        self._outputDirectory = outputDirectory
                        if not os.path.isdir(self._outputDirectory) or not os.path.exists(self._outputDirectory):
                                self.addError("The output directory {outputDirectory} either does not exist or \
                                is not a valid directory.".format(outputDirectory=self._outputDirectory))
                        if not os.access(self._outputDirectory, os.W_OK):
                                self.addError("Reposcanner does not have permissions to write to the output directory \
                                {outputDirectory}.".format(outputDirectory=self._outputDirectory))
                                
                except Exception as exception:
                        self.addError("Encountered an unexpected exception \
                        while parsing output directory \
                        {outputDirectory}: {exception}".format(outputDirectory=self._outputDirectory,
                        exception=exception))
                        
        def getOutputDirectory(self):
                return self._outputDirectory
                
        def criteriaFunction(self,entity):
                """
                Classes that inherit from AnalysisRequestModel must
                override the criteriaFunction to describe the data
                objects that the analysis expects to work with. By
                default, this function returns True, which means
                that the analysis will get all of the data held in
                ReposcannerManager's DataEntityStore.
                 
                
                entity: A ReposcannerDataEntity object. This function 
                should return True if the entity will be used in the
                analysis and False otherwise.
                """
                return True
                
        def getDataCriteria(self):
                """
                This is called to get the criteria function, which is passed
                to DataEntityStore.getByCriteria() to retrieve the data which
                is needed by the analysis.
                """
                return self.criteriaFunction
                
        def fetchDataFromStore(self,store):
                """
                This is called by ManagerTask.process() prior to running an analysis request.
                It loads any data that fits the request's criteria into the request.
                
                store: A DataEntityStore instance.
                """
                for entity in store.getByCriteria(self.getDataCriteria()):
                        self._data.append(entity)
                
        def getData(self):
                """
                Get any stored data associated with this request.
                Called by the DataAnalysis instance responsible for handling the request.
                """
                return self._data
                

class RoutineRequestModel(BaseRequestModel):
        """
        The base class for all routine request models. The frontend is responsible for phrasing their requests in the
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
                super().__init__()
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
                        if not os.access(self._outputDirectory, os.W_OK):
                                self.addError("Reposcanner does not have permissions to write to the output directory \
                                {outputDirectory}.".format(outputDirectory=self._outputDirectory))
                                
                except Exception as exception:
                        self.addError("Encountered an unexpected exception \
                        while parsing output directory \
                        {outputDirectory}: {exception}".format(outputDirectory=self._outputDirectory,
                        exception=exception))
                
                
        def getRepositoryLocation(self):
                return self._repositoryLocation
                
        def getOutputDirectory(self):
                return self._outputDirectory

        @classmethod
        def isRoutineRequestType(cls):
                return True
                

class OnlineRoutineRequest(RoutineRequestModel):
        """
        The base class for requests to routines that use an online API to compute results. 
        Request classes for OnlineRepositoryRoutine should inherit from this class.
        """
        
        @classmethod      
        def requiresOnlineAPIAccess(cls):
                """
                Tells the caller whether this request requires access to an online
                version control API.
                """
                return True
        
        def __init__(self,repositoryURL,outputDirectory,username=None,password=None,token=None,keychain=None):
                """
                Additional Parameters:
                
                username (@input): A string containing the client's handle.
                
                password (@input): A string containing the client's password.
                
                token (@input): A string containing a token associated with the user's account.
                
                keychain (@input): A CredentialKeychain object. The caller can pass a keychain as an
                        alternative to passing the username/password/token directly. If a keychain is
                        passed to the constructor, any other credential inputs are ignored.
                """
                super().__init__(repositoryURL,outputDirectory)
                
                self._credentials = None
                factory = gitEntities.GitEntityFactory()
                if keychain is None:
                        try:
                                self._credentials = factory.createVersionControlPlatformCredentials(
                                        username=username,
                                        password=password,
                                        token=token)
                        except Exception as exception:
                                self.addError("Encountered an unexpected exception \
                                while constructing credentials object: {exception}".format(exception=exception))
                else:
                        self._credentials = keychain.lookup(self.getRepositoryLocation())
                        if self._credentials is None:
                                 self.addError("Failed to find a matching set of credentials \
                                 on the keychain (out of {numberOfCredentials} credentials) corresponding to the URL of the repository ({URL}).".format(numberOfCredentials=len(keychain),URL=repositoryURL))
                        
        def getCredentials(self):
                return self._credentials
                
class OfflineRoutineRequest(RoutineRequestModel):
        """
        The base class for requests to routines that operate on an offline clone to compute results. 
        Request classes for OfflineRepositoryRoutine should inherit from this class.
        """
        
        @classmethod      
        def requiresOnlineAPIAccess(cls):
                """
                Tells the caller whether this request requires access to an online
                version control API.
                """
                return False
        
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
            return Path(self._workspaceDirectory) \
                      / "{repoOwner}_{repoName}".format(
                          repoOwner=self.getRepositoryLocation().getOwner(),
                          repoName=self.getRepositoryLocation().getRepositoryName())
                
        def getWorkspaceDirectory(self):
                return self._workspaceDirectory

