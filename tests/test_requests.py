import pytest
import reposcanner.requests as requests
from reposcanner.git import CredentialKeychain
from pathlib import Path
import platform


def test_AnalysisRequestModel_isDirectlyConstructible() -> None:
    analysisRequest = requests.AnalysisRequestModel(outputDirectory="./")


def test_AnalysisRequestModel_hasNoErrorsForValidInput() -> None:
    analysisRequest = requests.AnalysisRequestModel(outputDirectory="./")
    assert(not analysisRequest.hasErrors())


def test_AnalysisRequestModel_passingGarbageOutputDirectoryIsAnError() -> None:
    analysisRequest = requests.AnalysisRequestModel(outputDirectory=42)  # type: ignore
    assert(analysisRequest.hasErrors())


def test_AnalysisRequestModel_passingNonexistentOutputDirectoryIsAnError() -> None:
    analysisRequest = requests.AnalysisRequestModel(
        outputDirectory="./nonexistentDirectory/")
    assert(analysisRequest.hasErrors())


def test_AnalysisRequestModel_passingOutputDirectoryThatCannotBeWrittenToIsAnError() -> None:
    # This test is specific to Mac and Linux environments, so we'll skip it when running
    # this test in a Windows environment.
    if platform.system() == 'Windows':
        return
    analysisRequest = requests.AnalysisRequestModel(outputDirectory="/")
    assert(analysisRequest.hasErrors())


def test_AnalysisRequestModel_defaultDataCriteriaAcceptsLiterallyEverything() -> None:
    analysisRequest = requests.AnalysisRequestModel(outputDirectory="./")
    assert(analysisRequest.getDataCriteria() == analysisRequest.criteriaFunction)
    assert(analysisRequest.criteriaFunction("garbage") is True)  # type: ignore
    assert(analysisRequest.criteriaFunction(42) is True)  # type: ignore
    assert(analysisRequest.criteriaFunction(analysisRequest) is True)  # type: ignore


def test_ExternalCommandLineToolRoutineRequest_isDirectlyConstructible() -> None:
    requests.ExternalCommandLineToolRoutineRequest(outputDirectory="./")


def test_ExternalCommandLineToolRoutineRequest_hasNoErrorsForValidInput() -> None:
    commandLineToolRequest = requests.ExternalCommandLineToolRoutineRequest(
        outputDirectory="./")
    assert(not commandLineToolRequest.hasErrors())


def test_ExternalCommandLineToolRoutineRequest_passingOutputDirectoryThatCannotBeWrittenToIsAnError() -> None:
    # This test is specific to Mac and Linux environments, so we'll skip it when running
    # this test in a Windows environment.
    if platform.system() == 'Windows':
        return
    commandLineToolRequest = requests.ExternalCommandLineToolRoutineRequest(
        outputDirectory="/")
    assert(commandLineToolRequest.hasErrors())


def test_ExternalCommandLineToolRoutineRequest_canStoreOutputDirectory() -> None:
    commandLineToolRequest = requests.ExternalCommandLineToolRoutineRequest(
        outputDirectory="./")
    assert(commandLineToolRequest.getOutputDirectory() == "./")


def test_RepositoryRoutineRequestModel_isDirectlyConstructible() -> None:
    requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./")


def test_RepositoryRoutineRequestModel_hasNoErrorsForValidInput() -> None:
    request = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./")
    assert(not request.hasErrors())


def test_RepositoryRoutineRequestModel_passingOutputDirectoryThatCannotBeWrittenToIsAnError() -> None:
    # This test is specific to Mac and Linux environments, so we'll skip it when running
    # this test in a Windows environment.
    if platform.system() == 'Windows':
        return
    request = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo", outputDirectory="/")
    assert(request.hasErrors())


def test_RepositoryRoutineRequestModel_canGenerateAndStoreRepositoryLocation() -> None:
    request = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./")
    location = request.getRepositoryLocation()
    assert(location is not None)
    assert(location.isRecognizable())
    assert(location.getOwner() == "owner")
    assert(location.getRepositoryName() == "repo")


def test_RepositoryRoutineRequestModel_badURLMeansError() -> None:
    requestA = requests.RepositoryRoutineRequestModel(
        repositoryURL="garbage", outputDirectory="./")
    assert(requestA.hasErrors())

    requestB = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://unrecognizedhost.org/owner/repo", outputDirectory="./")
    assert(requestB.hasErrors())

    requestC = requests.RepositoryRoutineRequestModel(
        repositoryURL=None, outputDirectory="./")  # type: ignore
    assert(requestC.hasErrors())


def test_RepositoryRoutineRequestModel_canStoreOutputDirectory() -> None:
    request = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo", outputDirectory="./")
    assert(request.getOutputDirectory() == "./")


def test_RepositoryRoutineRequestModel_badOutputDirectoryMeansError() -> None:
    requestA = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo", outputDirectory=None)  # type: ignore
    assert(requestA.hasErrors())

    requestB = requests.RepositoryRoutineRequestModel(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./nonexistent/directory/")
    assert(requestB.hasErrors())


def test_OnlineRoutineRequest_isDirectlyConstructible() -> None:
    requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                                  outputDirectory="./",
                                  token="ab5571mc1")


def test_OnlineRoutineRequest_canPassKeychainToConstructor() -> None:
    credentialsDictionary = {}
    entry = {"url": "https://github.com/", "token": "ab341m32"}
    credentialsDictionary["platform"] = entry
    keychain = CredentialKeychain(credentialsDictionary=credentialsDictionary)
    requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                                  outputDirectory="./",
                                  keychain=keychain)


def test_OnlineRoutineRequest_canStoreValidCredentials() -> None:
    requestA = requests.OnlineRoutineRequest(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        token="ab5571mc1")
    assert(not requestA.hasErrors())
    credentialsA = requestA.getCredentials()
    assert(credentialsA is not None)
    assert(credentialsA.hasTokenAvailable())
    assert(credentialsA.getToken() == "ab5571mc1")

    requestB = requests.OnlineRoutineRequest(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        username="argyle",
        password="luggage")
    assert(not requestB.hasErrors())
    credentialsB = requestB.getCredentials()
    assert(credentialsB is not None)
    assert(credentialsB.hasUsernameAndPasswordAvailable())
    assert(credentialsB.getUsername() == "argyle")
    assert(credentialsB.getPassword() == "luggage")


def test_OnlineRoutineRequest_canStoreValidCredentialsViaKeychain() -> None:
    credentialsDictionary = {}
    entry = {"url": "https://github.com/", "token": "ab341m32"}
    credentialsDictionary["platform"] = entry

    keychain = CredentialKeychain(credentialsDictionary=credentialsDictionary)
    request = requests.OnlineRoutineRequest(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        keychain=keychain)
    assert(not request.hasErrors())
    credentials = request.getCredentials()
    assert(credentials is not None)
    assert(credentials.hasTokenAvailable())
    assert(credentials.getToken() == "ab341m32")


def test_OnlineRoutineRequest_keychainTakesPrecedenceOverOtherInputs() -> None:
    credentialsDictionary = {}
    entry = {"url": "https://github.com/", "token": "ab341m32"}
    credentialsDictionary["platform"] = entry

    keychain = CredentialKeychain(credentialsDictionary=credentialsDictionary)
    request = requests.OnlineRoutineRequest(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        token="qq4132c",
        keychain=keychain)
    assert(not request.hasErrors())
    credentials = request.getCredentials()
    assert(credentials is not None)
    assert(credentials.hasTokenAvailable())
    assert(credentials.getToken() == "ab341m32")


def test_OnlineRoutineRequest_doesNotSwitchToOtherCredentialsIfKeychainLacksThem() -> None:
    credentialsDictionary = {}
    entry = {"url": "https://gitlab.com/", "token": "ab341m32"}
    credentialsDictionary["platform"] = entry

    keychain = CredentialKeychain(credentialsDictionary=credentialsDictionary)
    request = requests.OnlineRoutineRequest(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        token="qq4132c",
        keychain=keychain)
    assert(request.hasErrors())


def test_OnlineRoutineRequest_badCredentialsMeansError() -> None:
    requestA = requests.OnlineRoutineRequest(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        token=None)
    assert(requestA.hasErrors())

    requestB = requests.OnlineRoutineRequest(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        username="argyle",
        password=None)
    assert(requestB.hasErrors())

    requestC = requests.OnlineRoutineRequest(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        username=None,
        password="luggage")
    assert(requestC.hasErrors())


def test_OfflineRoutineRequest_isDirectlyConstructible() -> None:
    requests.OfflineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                                   outputDirectory="./",
                                   workspaceDirectory="./")


def test_OfflineRoutineRequest_canStoreValidWorkspaceDirectory() -> None:
    request = requests.OfflineRoutineRequest(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        workspaceDirectory="./")
    assert(not request.hasErrors())
    assert(request.getWorkspaceDirectory() == "./")


def test_OfflineRoutineRequest_cloneDirectoryIsBasedOnWorkspaceDirectory() -> None:
    request = requests.OfflineRoutineRequest(
        repositoryURL="https://github.com/scikit/scikit-data",
        outputDirectory="./outputs/",
        workspaceDirectory="./workspace")
    assert(request.getCloneDirectory() == Path("./workspace/scikit_scikit-data"))


def test_OfflineRoutineRequest_badWorkspaceDirectoryMeansError() -> None:
    requestA = requests.OfflineRoutineRequest(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        workspaceDirectory=None)  # type: ignore
    assert(requestA.hasErrors())

    requestB = requests.OfflineRoutineRequest(
        repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        workspaceDirectory="./nonexistent/directory")
    assert(requestB.hasErrors())
