import pytest
import reposcanner.routines as routines
import reposcanner.requests as requests

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
        
        