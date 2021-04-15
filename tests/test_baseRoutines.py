import pytest
from reposcanner.git import GitEntityFactory
import reposcanner.routines as routines
import reposcanner.requests as requests
import reposcanner.response as responses

def test_RepositoryRoutine_isConstructibleWithMockImplementation(mocker):
        mocker.patch.multiple(routines.RepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.RepositoryRoutine()
        
def test_RepositoryRoutine_runCanReturnResponse(mocker):
        mocker.patch.multiple(routines.RepositoryRoutine,__abstractmethods__=set())
        def executeGeneratesResponse(self,request):
                factory = responses.ResponseFactory()
                response = factory.createSuccessResponse()
                return response
        routines.RepositoryRoutine.execute = executeGeneratesResponse
        genericRoutine = routines.RepositoryRoutine()
        genericRequest = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        response = genericRoutine.run(genericRequest)
        assert(response.wasSuccessful())
        
def test_RepositoryRoutine_exportCanAddAttachments(mocker):
        mocker.patch.multiple(routines.RepositoryRoutine,__abstractmethods__=set())
        def executeGeneratesResponse(self,request):
                factory = responses.ResponseFactory()
                response = factory.createSuccessResponse(attachments=[])
                response.addAttachment("data")
                return response
        
        routines.RepositoryRoutine.execute = executeGeneratesResponse
        genericRoutine = routines.RepositoryRoutine()
        genericRequest = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        response = genericRoutine.run(genericRequest)
        assert(response.wasSuccessful())
        assert(response.hasAttachments())
        assert(len(response.getAttachments()) == 1)
        

def test_OnlineRepositoryRoutine_isConstructibleWithMockImplementation(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.OfflineRepositoryRoutine()
        
def test_OfflineRepositoryRoutine_inabilityToHandleRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OfflineRepositoryRoutine,__abstractmethods__=set())
        def canNeverHandleRequest(self, request):
            return False
        originalCanHandleRequest = routines.OfflineRepositoryRoutine.canHandleRequest
        routines.OfflineRepositoryRoutine.canHandleRequest = canNeverHandleRequest
        genericRoutine = routines.OfflineRepositoryRoutine()
        
        genericRequest = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The routine was passed a request of the wrong type.")
        routines.OfflineRepositoryRoutine.canHandleRequest = originalCanHandleRequest
        
     
def test_OfflineRepositoryRoutine_errorsInRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OfflineRepositoryRoutine,__abstractmethods__=set())
        def canAlwaysHandleRequest(self, request):
            return True
        originalCanHandleRequest = routines.OfflineRepositoryRoutine.canHandleRequest
        routines.OfflineRepositoryRoutine.canHandleRequest = canAlwaysHandleRequest
        genericRoutine = routines.OfflineRepositoryRoutine()
        
        genericRequest = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        genericRequest.addError(message="Something has gone horribly wrong.")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The request had errors in it and cannot be processed.")
        routines.OfflineRepositoryRoutine.canHandleRequest = originalCanHandleRequest
        

def test_OnlineRepositoryRoutine_isConstructibleWithMockImplementation(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryRoutine()
        
def test_OnlineRepositoryRoutine_inabilityToHandleRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        def canNeverHandleRequest(self, request):
            return False
        originalCanHandleRequest = routines.OnlineRepositoryRoutine.canHandleRequest
        routines.OnlineRepositoryRoutine.canHandleRequest = canNeverHandleRequest
        genericRoutine = routines.OnlineRepositoryRoutine()
        
        genericRequest = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The routine was passed a request of the wrong type.")
        routines.OnlineRepositoryRoutine.canHandleRequest = originalCanHandleRequest
        
def test_OnlineRepositoryRoutine_errorsInRequestResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        def canAlwaysHandleRequest(self, request):
            return True
        originalCanHandleRequest = routines.OnlineRepositoryRoutine.canHandleRequest
        routines.OnlineRepositoryRoutine.canHandleRequest = canAlwaysHandleRequest
        genericRoutine = routines.OnlineRepositoryRoutine()
        
        genericRequest = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        genericRequest.addError(message="Something has gone horribly wrong.")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "The request had errors in it and cannot be processed.")
        routines.OnlineRepositoryRoutine.canHandleRequest = originalCanHandleRequest
       
def test_OnlineRepositoryRoutine_inabilityOfSessionCreatorToHandleRepositoryResultsInFailureResponse(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        def canAlwaysHandleRequest(self, request):
            return True
        originalCanHandleRequest = routines.OnlineRepositoryRoutine.canHandleRequest
        routines.OnlineRepositoryRoutine.canHandleRequest = canAlwaysHandleRequest
        genericRoutine = routines.OnlineRepositoryRoutine()
        
        gitEntityFactory = GitEntityFactory()
        emptyAPICreator = gitEntityFactory.createVCSAPISessionCompositeCreator()
        genericRoutine.sessionCreator = emptyAPICreator
        
        genericRequest = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        response = genericRoutine.run(genericRequest)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert("to handle the platform of the repository" in response.getMessage())
        routines.OnlineRepositoryRoutine.canHandleRequest = originalCanHandleRequest
        
def test_OnlineRepositoryRoutine_sessionCreatorSupportsGitHub(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryRoutine()
        sessionCreator = genericRoutine.sessionCreator
        genericGitHubRequest = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        assert(sessionCreator.canHandleRepository(genericGitHubRequest.getRepositoryLocation()))
        
def test_OnlineRepositoryRoutine_sessionCreatorSupportsGitlab(mocker):
        mocker.patch.multiple(routines.OnlineRepositoryRoutine,__abstractmethods__=set())
        genericRoutine = routines.OnlineRepositoryRoutine()
        sessionCreator = genericRoutine.sessionCreator
        genericGitlabRequest = requests.RoutineRequestModel(repositoryURL="https://gitlab.com/owner/repo",outputDirectory="./")
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
        
                        


        
        