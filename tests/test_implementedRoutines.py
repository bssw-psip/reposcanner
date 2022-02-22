import pytest
import reposcanner.contrib as contributionRoutines
import reposcanner.requests
        
def test_ContributorAccountListRoutineRequest_isDirectlyConstructible():
        request = contributionRoutines.ContributorAccountListRoutineRequest(repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        token = "ab5571mc1")

def test_ContributorAccountListRoutine_isDirectlyConstructible():
        routine = contributionRoutines.ContributorAccountListRoutine()
        
def test_ContributorAccountListRoutine_hasMatchingRequestType():
        routine = contributionRoutines.ContributorAccountListRoutine()
        assert(routine.getRequestType() == contributionRoutines.ContributorAccountListRoutineRequest )
        
def test_ContributorAccountListRoutine_canHandleAppropriateRequest():
        request = contributionRoutines.ContributorAccountListRoutineRequest(repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        token = "ab5571mc1")
        routine = contributionRoutines.ContributorAccountListRoutine()
        assert(routine.canHandleRequest(request))
        
def test_ContributorAccountListRoutine_willRejectInAppropriateRequest():
        request = reposcanner.requests.BaseRequestModel()
        routine = contributionRoutines.ContributorAccountListRoutine()
        
        assert(not isinstance(request, routine.getRequestType()))
        assert(not routine.canHandleRequest(request))
        




        
