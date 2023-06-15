import pytest
from reposcanner.git import GitEntityFactory
import reposcanner.routines as routines
import reposcanner.requests as requests
import reposcanner.response as responses
from typing import Any, Type


# TODO: These tests use monkeypatching in a way that can affect other tests.
# The test will monkeypatch a method, do an assertion, and then restore the method.
# However, when the assertion fails, the method never gets restored.
# Then, unrelated tests will start to fail, which makes it harder to localize the error.
# Where possible, these tests should monkeypatch individual objects rather than classes.
# Rather than:
#
#     originalMethod = Clazz.method
#     Clazz.method = newMethod
#     obj = Clazz()
#     assert foo(obj)
#     Clazz.method = originalMethod
#
# I propose:
#
#     obj = Clazz()
#     obj.method = newMethod
#     assert foo(obj)
#
# Clazz remains unaffected.

# mypy: disable-error-code="abstract,method-assign" 


def test_RepositoryRoutine_isConstructibleWithMockImplementation(mocker: Any) -> None:
    mocker.patch.multiple(routines.RepositoryRoutine, __abstractmethods__=set())
    genericRoutine = routines.RepositoryRoutine()  # type: ignore


def test_RepositoryRoutine_runCanReturnResponse(mocker: Any) -> None:
    mocker.patch.multiple(routines.RepositoryRoutine, __abstractmethods__=set())

    def executeGeneratesResponse(
            self: routines.RepositoryRoutine,
            request: requests.RepositoryRoutineRequestModel,
    ) -> responses.ResponseModel:
        factory = responses.ResponseFactory()
        response = factory.createSuccessResponse()
        return response
    routines.RepositoryRoutine.execute = executeGeneratesResponse  # type: ignore
    genericRoutine = routines.RepositoryRoutine()  # type: ignore
    genericRequest = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./")
    response = genericRoutine.run(genericRequest)
    assert(response.wasSuccessful())


def test_RepositoryRoutine_exportCanAddAttachments(mocker: Any) -> None:
    mocker.patch.multiple(routines.RepositoryRoutine, __abstractmethods__=set())

    def executeGeneratesResponse(
            self: routines.DataMiningRoutine,
            request: requests.BaseRequestModel,
    ) -> responses.ResponseModel:
        factory = responses.ResponseFactory()
        response = factory.createSuccessResponse(attachments=[])
        response.addAttachment("data")
        return response

    routines.RepositoryRoutine.execute = executeGeneratesResponse
    genericRoutine = routines.RepositoryRoutine()
    genericRequest = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./")
    response = genericRoutine.run(genericRequest)
    assert(response.wasSuccessful())
    assert(response.hasAttachments())
    assert(len(response.getAttachments()) == 1)


def test_RepositoryRoutine_canSetConfigurationParameters(mocker: Any) -> None:
    mocker.patch.multiple(routines.RepositoryRoutine, __abstractmethods__=set())
    genericRoutine = routines.RepositoryRoutine()
    configurationParameters = {"verbose": True, "debug": False}
    assert(not genericRoutine.hasConfigurationParameters())
    assert(genericRoutine.getConfigurationParameters() is None)
    genericRoutine.setConfigurationParameters(configurationParameters)
    assert(genericRoutine.hasConfigurationParameters())
    assert(genericRoutine.getConfigurationParameters() == configurationParameters)


def test_ExternalCommandLineToolRoutine_isConstructibleWithMockImplementation(mocker: Any) -> None:
    mocker.patch.multiple(
        routines.ExternalCommandLineToolRoutine,
        __abstractmethods__=set())
    genericExternalCommandLineToolRoutine = routines.ExternalCommandLineToolRoutine() # type: ignore


def test_ExternalCommandLineToolRoutine_runCanReturnResponses(mocker: Any) -> None:
    mocker.patch.multiple(
        routines.ExternalCommandLineToolRoutine,
        __abstractmethods__=set())

    def supportsGenericRequestType(self: routines.DataMiningRoutine) -> Type[requests.BaseRequestModel]:
        return requests.ExternalCommandLineToolRoutineRequest

    def implementationGeneratesResponse(
            self: routines.ExternalCommandLineToolRoutine,
            request: requests.BaseRequestModel
    ) -> responses.ResponseModel:
        factory = responses.ResponseFactory()
        response = factory.createSuccessResponse(attachments=[])
        response.addAttachment("data")
        return response

    routines.ExternalCommandLineToolRoutine.getRequestType = supportsGenericRequestType
    routines.ExternalCommandLineToolRoutine.commandLineToolImplementation = implementationGeneratesResponse
    genericExternalCommandLineToolRoutine = routines.ExternalCommandLineToolRoutine()
    genericRequest = requests.ExternalCommandLineToolRoutineRequest(
        outputDirectory="./")
    response = genericExternalCommandLineToolRoutine.run(genericRequest)
    assert(response.wasSuccessful())
    assert(response.hasAttachments())
    assert(len(response.getAttachments()) == 1)


def test_ExternalCommandLineToolRoutine_canSetConfigurationParameters(mocker: Any) -> None:
    mocker.patch.multiple(
        routines.ExternalCommandLineToolRoutine,
        __abstractmethods__=set())
    genericRoutine = routines.ExternalCommandLineToolRoutine()
    configurationParameters = {"verbose": True, "debug": False}
    assert(not genericRoutine.hasConfigurationParameters())
    assert(genericRoutine.getConfigurationParameters() is None)
    genericRoutine.setConfigurationParameters(configurationParameters)
    assert(genericRoutine.hasConfigurationParameters())
    assert(genericRoutine.getConfigurationParameters() == configurationParameters)


def test_OfflineRepositoryRoutine_isConstructibleWithMockImplementation(mocker: Any) -> None:
    mocker.patch.multiple(routines.OfflineRepositoryRoutine, __abstractmethods__=set())
    genericRoutine = routines.OfflineRepositoryRoutine()


def test_OfflineRepositoryRoutine_inabilityToHandleRequestResultsInFailureResponse(
        mocker: Any) -> None:
    mocker.patch.multiple(routines.OfflineRepositoryRoutine, __abstractmethods__=set())

    def canNeverHandleRequest(self: routines.DataMiningRoutine, request: requests.BaseRequestModel) -> bool:
        return False
    originalCanHandleRequest = routines.OfflineRepositoryRoutine.canHandleRequest
    routines.OfflineRepositoryRoutine.canHandleRequest = canNeverHandleRequest
    genericRoutine = routines.OfflineRepositoryRoutine()

    genericRequest = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./")
    response = genericRoutine.run(genericRequest)
    assert(not response.wasSuccessful())
    assert(response.hasMessage())
    assert(response.getMessage() == "The routine was passed a request of the wrong type.")
    routines.OfflineRepositoryRoutine.canHandleRequest = originalCanHandleRequest


def test_OfflineRepositoryRoutine_errorsInRequestResultsInFailureResponse(mocker: Any) -> None:
    mocker.patch.multiple(routines.OfflineRepositoryRoutine, __abstractmethods__=set())

    def canAlwaysHandleRequest(self: routines.DataMiningRoutine, request: requests.BaseRequestModel) -> bool:
        return True
    originalCanHandleRequest = routines.OfflineRepositoryRoutine.canHandleRequest
    routines.OfflineRepositoryRoutine.canHandleRequest = canAlwaysHandleRequest
    genericRoutine = routines.OfflineRepositoryRoutine()

    genericRequest = requests.OfflineRoutineRequest(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./out", workspaceDirectory="./workspace")
    genericRequest.addError(message="Something has gone horribly wrong.")
    response = genericRoutine.run(genericRequest)
    assert(not response.wasSuccessful())
    assert(response.hasMessage())
    assert(response.getMessage() == "The request had errors in it and cannot be processed.")
    routines.OfflineRepositoryRoutine.canHandleRequest = originalCanHandleRequest


def test_OnlineRepositoryRoutine_isConstructibleWithMockImplementation(mocker: Any) -> None:
    mocker.patch.multiple(routines.OnlineRepositoryRoutine, __abstractmethods__=set())
    genericRoutine = routines.OnlineRepositoryRoutine()


def test_OnlineRepositoryRoutine_inabilityToHandleRequestResultsInFailureResponse(
        mocker: Any) -> None:
    mocker.patch.multiple(routines.OnlineRepositoryRoutine, __abstractmethods__=set())

    def canNeverHandleRequest(self: routines.DataMiningRoutine, request: requests.BaseRequestModel) -> bool:
        return False
    originalCanHandleRequest = routines.OnlineRepositoryRoutine.canHandleRequest
    routines.OnlineRepositoryRoutine.canHandleRequest = canNeverHandleRequest
    genericRoutine = routines.OnlineRepositoryRoutine()

    genericRequest = requests.OnlineRoutineRequest(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./out")
    response = genericRoutine.run(genericRequest)
    assert(not response.wasSuccessful())
    assert(response.hasMessage())
    assert(response.getMessage() == "The routine was passed a request of the wrong type.")
    routines.OnlineRepositoryRoutine.canHandleRequest = originalCanHandleRequest


def test_OnlineRepositoryRoutine_errorsInRequestResultsInFailureResponse(mocker: Any) -> None:
    mocker.patch.multiple(routines.OnlineRepositoryRoutine, __abstractmethods__=set())

    def canAlwaysHandleRequest(self: routines.DataMiningRoutine, request: requests.BaseRequestModel) -> bool:
        return True
    originalCanHandleRequest = routines.OnlineRepositoryRoutine.canHandleRequest
    routines.OnlineRepositoryRoutine.canHandleRequest = canAlwaysHandleRequest
    genericRoutine = routines.OnlineRepositoryRoutine()

    genericRequest = requests.OnlineRoutineRequest(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./")
    genericRequest.addError(message="Something has gone horribly wrong.")
    response = genericRoutine.run(genericRequest)
    assert(not response.wasSuccessful())
    assert(response.hasMessage())
    assert(response.getMessage() == "The request had errors in it and cannot be processed.")
    routines.OnlineRepositoryRoutine.canHandleRequest = originalCanHandleRequest


def test_OnlineRepositoryRoutine_inabilityOfSessionCreatorToHandleRepositoryResultsInFailureResponse(
        mocker: Any) -> None:
    mocker.patch.multiple(routines.OnlineRepositoryRoutine, __abstractmethods__=set())

    def canAlwaysHandleRequest(self: routines.DataMiningRoutine, request: requests.BaseRequestModel) -> bool:
        return True
    originalCanHandleRequest = routines.OnlineRepositoryRoutine.canHandleRequest
    routines.OnlineRepositoryRoutine.canHandleRequest = canAlwaysHandleRequest
    genericRoutine = routines.OnlineRepositoryRoutine()

    gitEntityFactory = GitEntityFactory()
    emptyAPICreator = gitEntityFactory.createVCSAPISessionCompositeCreator()
    genericRoutine.sessionCreator = emptyAPICreator

    genericRequest = requests.OnlineRoutineRequest(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./", username="foo", password="bar")
    response = genericRoutine.run(genericRequest)
    assert(not response.wasSuccessful())
    assert(response.hasMessage())
    message = response.getMessage()
    assert(message is not None and "to handle the platform of the repository" in message)
    routines.OnlineRepositoryRoutine.canHandleRequest = originalCanHandleRequest


def test_OnlineRepositoryRoutine_sessionCreatorSupportsGitHub(mocker: Any) -> None:
    mocker.patch.multiple(routines.OnlineRepositoryRoutine, __abstractmethods__=set())
    genericRoutine = routines.OnlineRepositoryRoutine()
    sessionCreator = genericRoutine.sessionCreator
    genericGitHubRequest = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./")
    assert(sessionCreator.canHandleRepository(
        genericGitHubRequest.getRepositoryLocation()))


def test_OnlineRepositoryRoutine_sessionCreatorSupportsGitlab(mocker: Any) -> None:
    mocker.patch.multiple(routines.OnlineRepositoryRoutine, __abstractmethods__=set())
    genericRoutine = routines.OnlineRepositoryRoutine()
    sessionCreator = genericRoutine.sessionCreator
    genericGitlabRequest = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://gitlab.com/owner/repo", outputDirectory="./")
    assert(sessionCreator.canHandleRepository(
        genericGitlabRequest.getRepositoryLocation()))


def test_OnlineRepositoryRoutine_defaultGitHubImplementationReturnsFailedResponse(
        mocker: Any) -> None:
    mocker.patch.multiple(routines.OnlineRepositoryRoutine, __abstractmethods__=set())
    genericRoutine = routines.OnlineRepositoryRoutine()
    genericGitHubRequest = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./")
    response = genericRoutine.githubImplementation(request=genericGitHubRequest, session=None)
    assert(not response.wasSuccessful())
    message = response.getMessage()
    assert(message is not None)
    assert(message == "This routine has no implementation available \
                        to handle a GitHub repository.")


def test_OnlineRepositoryRoutine_defaultGitlabImplementationReturnsFailedResponse(
        mocker: Any) -> None:
    mocker.patch.multiple(routines.OnlineRepositoryRoutine, __abstractmethods__=set())
    genericRoutine = routines.OnlineRepositoryRoutine()
    genericGitlabRequest = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://gitlab.com/owner/repo", outputDirectory="./")
    response = genericRoutine.gitlabImplementation(request=genericGitlabRequest, session=None)
    assert(not response.wasSuccessful())
    message = response.getMessage()
    assert(message is not None)
    assert(message == "This routine has no implementation available \
                        to handle a Gitlab repository.")


def test_OnlineRepositoryRoutine_defaultBitbucketImplementationReturnsFailedResponse(
        mocker: Any) -> None:
    mocker.patch.multiple(routines.OnlineRepositoryRoutine, __abstractmethods__=set())
    genericBitbucketRequest = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://bitbucket.com/owner/repo", outputDirectory="./")
    genericRoutine = routines.OnlineRepositoryRoutine()
    response = genericRoutine.bitbucketImplementation(request=genericBitbucketRequest, session=None)
    assert(not response.wasSuccessful())
    assert(response.hasMessage())
    message = response.getMessage()
    assert(message is not None)
    assert(message == "This routine has no implementation available \
                        to handle a Bitbucket repository.")
