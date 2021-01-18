import pytest
from reposcanner.git import GitEntityFactory
import reposcanner.routines as routines
import reposcanner.requests as requests
import reposcanner.response as response

def test_OnlineRepositoryRoutine_isConstructibleWithMockImplementation(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.OfflineRepositoryRoutine()
        
def test_OfflineRepositoryRoutine_inabilityToHandleRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OfflineRepositoryRoutine,__abstractmethods__=set())
        def canNeverHandleRequest(self, request):
            return False
        routines.OfflineRepositoryRoutine.canHandleRequest = canNeverHandleRequest
        genericRoutine = routines.OfflineRepositoryRoutine()
        
        genericRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The routine was passed a request of the wrong type.")
        
        
def test_OfflineRepositoryRoutine_errorsInRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OfflineRepositoryRoutine,__abstractmethods__=set())
        def canAlwaysHandleRequest(self, request):
            return True
        routines.OfflineRepositoryRoutine.canHandleRequest = canAlwaysHandleRequest
        genericRoutine = routines.OfflineRepositoryRoutine()
        
        genericRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        genericRequest.addError(message="Something has gone horribly wrong.")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The request had errors in it and cannot be processed.")
        
        

def test_OnlineRepositoryRoutine_isConstructibleWithMockImplementation(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryRoutine()
        
def test_OnlineRepositoryRoutine_inabilityToHandleRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        def canNeverHandleRequest(self, request):
            return False
        routines.OnlineRepositoryRoutine.canHandleRequest = canNeverHandleRequest
        genericRoutine = routines.OnlineRepositoryRoutine()
        
        genericRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The routine was passed a request of the wrong type.")
        
def test_OnlineRepositoryRoutine_errorsInRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        def canAlwaysHandleRequest(self, request):
            return True
        routines.OnlineRepositoryRoutine.canHandleRequest = canAlwaysHandleRequest
        genericRoutine = routines.OnlineRepositoryRoutine()
        
        genericRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        genericRequest.addError(message="Something has gone horribly wrong.")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The request had errors in it and cannot be processed.")
        
def test_OnlineRepositoryRoutine_inabilityOfSessionCreatorToHandleRepositoryResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        def canAlwaysHandleRequest(self, request):
            return True
        routines.OnlineRepositoryRoutine.canHandleRequest = canAlwaysHandleRequest
        genericRoutine = routines.OnlineRepositoryRoutine()
        
        gitEntityFactory = GitEntityFactory()
        emptyAPICreator = gitEntityFactory.createVCSAPISessionCompositeCreator()
        genericRoutine.sessionCreator = emptyAPICreator
        
        genericRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert("to handle the platform of the repository" in response.getMessage())
        
        
def test_OnlineRepositoryRoutine_sessionCreatorSupportsGitHub(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryRoutine()
        sessionCreator = genericRoutine.sessionCreator
        genericGitHubRequest = requests.BaseRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        assert(sessionCreator.canHandleRepository(genericGitHubRequest.getRepositoryLocation()))
        
def test_OnlineRepositoryRoutine_sessionCreatorSupportsGitlab(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryRoutine()
        sessionCreator = genericRoutine.sessionCreator
        genericGitlabRequest = requests.BaseRequestModel(repositoryURL="https://gitlab.com/owner/repo",outputDirectory="./")
        assert(sessionCreator.canHandleRepository(genericGitlabRequest.getRepositoryLocation()))


                        
def test_OnlineRepositoryRoutine_defaultGitHubImplementationReturnsFailedResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryRoutine()
        response = genericRoutine.githubImplementation(request=None,session=None)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "This routine has no implementation available \
                        to handle a GitHub repository.")
                        
def test_OnlineRepositoryRoutine_defaultGitlabImplementationReturnsFailedResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryRoutine()
        response = genericRoutine.gitlabImplementation(request=None,session=None)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "This routine has no implementation available \
                        to handle a Gitlab repository.")
                        
def test_OnlineRepositoryRoutine_defaultBitbucketImplementationReturnsFailedResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryRoutine()
        response = genericRoutine.bitbucketImplementation(request=None,session=None)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "This routine has no implementation available \
                        to handle a Bitbucket repository.")
        
                        


        
        