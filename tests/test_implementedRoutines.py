import pytest
import reposcanner.contrib as contributionRoutines
import reposcanner.requests


def test_CommitInfoMiningRoutineRequest_isDirectlyConstructible():
    request = contributionRoutines.CommitInfoMiningRoutineRequest(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./", workspaceDirectory="./")


def test_CommitInfoMiningRoutine_isDirectlyConstructible():
    routine = contributionRoutines.CommitInfoMiningRoutine()


def test_CommitInfoMiningRoutine_hasMatchingRequestType():
    routine = contributionRoutines.CommitInfoMiningRoutine()
    assert(routine.getRequestType() ==
           contributionRoutines.CommitInfoMiningRoutineRequest)


def test_CommitInfoMiningRoutine_canHandleAppropriateRequest():
    request = contributionRoutines.CommitInfoMiningRoutineRequest(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./", workspaceDirectory="./")
    routine = contributionRoutines.CommitInfoMiningRoutine()
    assert(routine.canHandleRequest(request))


def test_CommitInfoMiningRoutine_willRejectInAppropriateRequest():
    request = reposcanner.requests.BaseRequestModel()
    routine = contributionRoutines.CommitInfoMiningRoutine()

    assert(not isinstance(request, routine.getRequestType()))
    assert(not routine.canHandleRequest(request))
    

def test_CommitInfoMiningRoutine_hasDefaultConfigurationParameters():
    routine = contributionRoutines.CommitInfoMiningRoutine()
    assert(routine.hasConfigurationParameters())
    
def test_CommitInfoMiningRoutine_canSetConfigurationParametersUsingConstructor():
    configParameters = {
        "parallel" : True,
        "numberOfProcesses" : 5
    }
    routine = contributionRoutines.CommitInfoMiningRoutine(configParameters=configParameters)
    assert(routine.hasConfigurationParameters())
    configuration = routine.getConfigurationParameters()
    assert("parallel" in configuration and configuration["parallel"] == True)
    assert("numberOfProcesses" in configuration and configuration["numberOfProcesses"] == 5)
    
def test_CommitInfoMiningRoutine_canSetConfigurationParametersAfterConstruction():
    configParameters = {
        "parallel" : True,
        "numberOfProcesses" : 5
    }
    routine = contributionRoutines.CommitInfoMiningRoutine()
    routine.setConfigurationParameters(configParameters)
    configuration = routine.getConfigurationParameters()
    assert("parallel" in configuration and configuration["parallel"] == True)
    assert("numberOfProcesses" in configuration and configuration["numberOfProcesses"] == 5)
        
    
    
def test_CommitInfoMiningRoutine_defaultConfigParametersDisablesParallelExecution():
    routine = contributionRoutines.CommitInfoMiningRoutine()
    configuration = routine.getConfigurationParameters()
    assert("parallel" in configuration and configuration["parallel"] == False)
    assert("numberOfProcesses" in configuration and configuration["numberOfProcesses"] == 0)
    




def test_ContributorAccountListRoutineRequest_isDirectlyConstructible():
    request = contributionRoutines.ContributorAccountListRoutineRequest(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./", token="ab5571mc1")


def test_ContributorAccountListRoutine_isDirectlyConstructible():
    routine = contributionRoutines.ContributorAccountListRoutine()


def test_ContributorAccountListRoutine_hasMatchingRequestType():
    routine = contributionRoutines.ContributorAccountListRoutine()
    assert(routine.getRequestType() ==
           contributionRoutines.ContributorAccountListRoutineRequest)


def test_ContributorAccountListRoutine_canHandleAppropriateRequest():
    request = contributionRoutines.ContributorAccountListRoutineRequest(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./", token="ab5571mc1")
    routine = contributionRoutines.ContributorAccountListRoutine()
    assert(routine.canHandleRequest(request))


def test_ContributorAccountListRoutine_willRejectInAppropriateRequest():
    request = reposcanner.requests.BaseRequestModel()
    routine = contributionRoutines.ContributorAccountListRoutine()

    assert(not isinstance(request, routine.getRequestType()))
    assert(not routine.canHandleRequest(request))
