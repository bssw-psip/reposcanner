import pytest
from reposcanner.git import GitEntityFactory
import reposcanner.routines as routines
import reposcanner.requests as requests
import reposcanner.response as response

def test_OnlineRepositoryAnalysisRoutine_isConstructibleWithMockImplementation(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryAnalysisRoutine,__abstractmethods__=set())
        genericRoutine = routines.OfflineRepositoryAnalysisRoutine()
        
def test_OfflineRepositoryAnalysisRoutine_inabilityToHandleRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OfflineRepositoryAnalysisRoutine,__abstractmethods__=set())
        def canNeverHandleRequest(self, request):
            return False
        routines.OfflineRepositoryAnalysisRoutine.canHandleRequest = canNeverHandleRequest
        genericRoutine = routines.OfflineRepositoryAnalysisRoutine()
        
        genericRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The routine was passed a request of the wrong type.")
        
        
def test_OfflineRepositoryAnalysisRoutine_errorsInRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OfflineRepositoryAnalysisRoutine,__abstractmethods__=set())
        def canAlwaysHandleRequest(self, request):
            return True
        routines.OfflineRepositoryAnalysisRoutine.canHandleRequest = canAlwaysHandleRequest
        genericRoutine = routines.OfflineRepositoryAnalysisRoutine()
        
        genericRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        genericRequest.addError(message="Something has gone horribly wrong.")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The request had errors in it and cannot be processed.")
        
        

def test_OnlineRepositoryAnalysisRoutine_isConstructibleWithMockImplementation(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryAnalysisRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryAnalysisRoutine()
        
def test_OnlineRepositoryAnalysisRoutine_inabilityToHandleRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryAnalysisRoutine,__abstractmethods__=set())
        def canNeverHandleRequest(self, request):
            return False
        routines.OnlineRepositoryAnalysisRoutine.canHandleRequest = canNeverHandleRequest
        genericRoutine = routines.OnlineRepositoryAnalysisRoutine()
        
        genericRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The routine was passed a request of the wrong type.")
        
def test_OnlineRepositoryAnalysisRoutine_errorsInRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryAnalysisRoutine,__abstractmethods__=set())
        def canAlwaysHandleRequest(self, request):
            return True
        routines.OnlineRepositoryAnalysisRoutine.canHandleRequest = canAlwaysHandleRequest
        genericRoutine = routines.OnlineRepositoryAnalysisRoutine()
        
        genericRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        genericRequest.addError(message="Something has gone horribly wrong.")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The request had errors in it and cannot be processed.")
        
def test_OnlineRepositoryAnalysisRoutine_inabilityOfSessionCreatorToHandleRepositoryResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryAnalysisRoutine,__abstractmethods__=set())
        def canAlwaysHandleRequest(self, request):
            return True
        routines.OnlineRepositoryAnalysisRoutine.canHandleRequest = canAlwaysHandleRequest
        genericRoutine = routines.OnlineRepositoryAnalysisRoutine()
        
        gitEntityFactory = GitEntityFactory()
        emptyAPICreator = gitEntityFactory.createVCSAPISessionCompositeCreator()
        genericRoutine.sessionCreator = emptyAPICreator
        
        genericRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert("to handle the platform of the repository" in response.getMessage())
        
        
def test_OnlineRepositoryAnalysisRoutine_sessionCreatorSupportsGitHub(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryAnalysisRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryAnalysisRoutine()
        sessionCreator = genericRoutine.sessionCreator
        genericGitHubRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        assert(sessionCreator.canHandleRepository(genericGitHubRequest.getRepositoryLocation()))
        
def test_OnlineRepositoryAnalysisRoutine_sessionCreatorSupportsGitlab(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryAnalysisRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryAnalysisRoutine()
        sessionCreator = genericRoutine.sessionCreator
        genericGitlabRequest = requests.BaseRequestModel(repositoryURL="https://gitlab.com/owner/repo",outputDirectory="./")
        assert(sessionCreator.canHandleRepository(genericGitlabRequest.getRepositoryLocation()))


                        
def test_OnlineRepositoryAnalysisRoutine_defaultGitHubImplementationReturnsFailedResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryAnalysisRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryAnalysisRoutine()
        response = genericRoutine.githubImplementation(request=None,session=None)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "This routine has no implementation available \
                        to handle a GitHub repository.")
                        
def test_OnlineRepositoryAnalysisRoutine_defaultGitlabImplementationReturnsFailedResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryAnalysisRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryAnalysisRoutine()
        response = genericRoutine.gitlabImplementation(request=None,session=None)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "This routine has no implementation available \
                        to handle a Gitlab repository.")
                        
def test_OnlineRepositoryAnalysisRoutine_defaultBitbucketImplementationReturnsFailedResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryAnalysisRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryAnalysisRoutine()
        response = genericRoutine.bitbucketImplementation(request=None,session=None)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "This routine has no implementation available \
                        to handle a Bitbucket repository.")
        
                        


        
        