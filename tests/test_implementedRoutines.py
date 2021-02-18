import pytest
import reposcanner.contrib as contributionRoutines
import reposcanner.requests

"""
def test_ContributionPeriodRoutineRequest_isDirectlyConstructible():
        request = contributionRoutines.ContributionPeriodRoutineRequest(repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        workspaceDirectory="./")

def test_ContributionPeriodRoutine_isDirectlyConstructible():
        routine = contributionRoutines.ContributionPeriodRoutine()
        
def test_ContributionPeriodRoutine_canHandleAppropriateRequest():
        request = contributionRoutines.ContributionPeriodRoutineRequest(repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        workspaceDirectory="./")
        routine = contributionRoutines.ContributionPeriodRoutine()
        assert(routine.canHandleRequest(request))
        
def test_ContributionPeriodRoutine_willRejectInAppropriateRequest():
        request = reposcanner.requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        routine = contributionRoutines.ContributionPeriodRoutine()
        assert(not routine.canHandleRequest(request))
"""
        
def test_ContributorAccountListRoutineRequest_isDirectlyConstructible():
        request = contributionRoutines.ContributorAccountListRoutineRequest(repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        token = "ab5571mc1")

def test_ContributorAccountListRoutine_isDirectlyConstructible():
        routine = contributionRoutines.ContributorAccountListRoutine()
        
def test_ContributorAccountListRoutine_canHandleAppropriateRequest():
        request = contributionRoutines.ContributorAccountListRoutineRequest(repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        token = "ab5571mc1")
        routine = contributionRoutines.ContributorAccountListRoutine()
        assert(routine.canHandleRequest(request))
        
def test_ContributorAccountListRoutine_willRejectInAppropriateRequest():
        request = reposcanner.requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        routine = contributionRoutines.ContributorAccountListRoutine()
        assert(not routine.canHandleRequest(request))
        




        