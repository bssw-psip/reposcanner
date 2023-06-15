import pytest
import reposcanner.git as gitEntities
from typing import Dict, List


def test_RepositoryLocation_isConstructibleByFactory() -> None:
    factory = gitEntities.GitEntityFactory()
    repositoryLocation = factory.createRepositoryLocation(
        url="github.com/owner/repository")


def test_RepositoryLocation_isDirectlyConstructible() -> None:
    repositoryLocation = gitEntities.RepositoryLocation(
        url="github.com/owner/repository")


def test_RepositoryLocation_canStoreURL() -> None:
    url = "arbitrary.edu/repo/name"
    repositoryLocation = gitEntities.RepositoryLocation(url="arbitrary.edu/repo/name")
    assert(repositoryLocation.getURL() == url)


def test_RepositoryLocation_canIdentifyGitHubURLs() -> None:
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://github.com/Parallel-NetCDF/PnetCDF")
    assert(repositoryLocation.getVersionControlPlatform() ==
           gitEntities.RepositoryLocation.VersionControlPlatform.GITHUB)
    assert(repositoryLocation.getVersionControlHostType() ==
           gitEntities.RepositoryLocation.HostType.OFFICIAL)


def test_RepositoryLocation_canIdentifyGitlabURLs() -> None:
    repositoryLocationOfficial = gitEntities.RepositoryLocation(
        url="https://gitlab.com/exaalt/parsplice")
    assert(repositoryLocationOfficial.getVersionControlPlatform() ==
           gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)
    assert(repositoryLocationOfficial.getVersionControlHostType()
           == gitEntities.RepositoryLocation.HostType.OFFICIAL)

    repositoryLocationSelfHosted = gitEntities.RepositoryLocation(
        url="https://xgitlab.cels.anl.gov/darshan/darshan")
    assert(repositoryLocationSelfHosted.getVersionControlPlatform() ==
           gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)
    assert(repositoryLocationSelfHosted.getVersionControlHostType()
           == gitEntities.RepositoryLocation.HostType.SELFHOSTED)


def test_RepositoryLocation_canIdentifyBitbucketURLs() -> None:
    repositoryLocationOfficial = gitEntities.RepositoryLocation(
        url="https://bitbucket.org/berkeleylab/picsar")
    assert(repositoryLocationOfficial.getVersionControlPlatform() ==
           gitEntities.RepositoryLocation.VersionControlPlatform.BITBUCKET)
    assert(repositoryLocationOfficial.getVersionControlHostType()
           == gitEntities.RepositoryLocation.HostType.OFFICIAL)

    repositoryLocationSelfHosted = gitEntities.RepositoryLocation(
        url="https://bitbucket.hdfgroup.org/scm/hdffv/hdf5")
    assert(repositoryLocationSelfHosted.getVersionControlPlatform() ==
           gitEntities.RepositoryLocation.VersionControlPlatform.BITBUCKET)
    assert(repositoryLocationSelfHosted.getVersionControlHostType()
           == gitEntities.RepositoryLocation.HostType.SELFHOSTED)


def test_RepositoryLocation_unrecognizedURLsAreUnknown() -> None:
    repositoryLocationA = gitEntities.RepositoryLocation(
        url="http://flash.uchicago.edu/site/flashcode/coderequest/")
    assert(repositoryLocationA.getVersionControlPlatform() ==
           gitEntities.RepositoryLocation.VersionControlPlatform.UNKNOWN)
    assert(repositoryLocationA.getVersionControlHostType() ==
           gitEntities.RepositoryLocation.HostType.UNKNOWN)

    repositoryLocationB = gitEntities.RepositoryLocation(
        url="https://code-int.ornl.gov/exnihilo/Exnihilo")
    assert(repositoryLocationB.getVersionControlPlatform() ==
           gitEntities.RepositoryLocation.VersionControlPlatform.UNKNOWN)
    assert(repositoryLocationB.getVersionControlHostType() ==
           gitEntities.RepositoryLocation.HostType.UNKNOWN)


def test_RepositoryLocation_expectedPlatformOverridesActualPlatform() -> None:
    repositoryLocationA = gitEntities.RepositoryLocation(
        url="https://code-int.ornl.gov/exnihilo/Exnihilo",
        expectedPlatform=gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)
    assert(repositoryLocationA.getVersionControlPlatform() ==
           gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)

    repositoryLocationB = gitEntities.RepositoryLocation(
        url="https://github.com/Parallel-NetCDF/PnetCDF",
        expectedPlatform=gitEntities.RepositoryLocation.VersionControlPlatform.BITBUCKET)
    assert(repositoryLocationB.getVersionControlPlatform() ==
           gitEntities.RepositoryLocation.VersionControlPlatform.BITBUCKET)


def test_RepositoryLocation_providingPlatformButNotHostTypeMakesItUnknown() -> None:
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://code-int.ornl.gov/exnihilo/Exnihilo",
        expectedPlatform=gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)
    assert(repositoryLocation.getVersionControlHostType() ==
           gitEntities.RepositoryLocation.HostType.UNKNOWN)


def test_RepositoryLocation_providingBothPlatformAndHostTypeRespectsBothChoices() -> None:
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://code-int.ornl.gov/exnihilo/Exnihilo",
        expectedPlatform=gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB,
        expectedHostType=gitEntities.RepositoryLocation.HostType.SELFHOSTED)
    assert(repositoryLocation.getVersionControlPlatform() ==
           gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)
    assert(repositoryLocation.getVersionControlHostType() ==
           gitEntities.RepositoryLocation.HostType.SELFHOSTED)


def test_RepositoryLocation_providingBothOwnerAndRepositoryNameRespectsBothChoices() -> None:
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://bitbucket.hdfgroup.org/scm/hdffv/hdf5",
        expectedOwner="hdffv",
        expectedRepositoryName="hdf5")
    assert(repositoryLocation.getOwner() == "hdffv")
    assert(repositoryLocation.getRepositoryName() == "hdf5")


def test_RepositoryLocation_canParseOwnerAndNameOfGitHubRepository() -> None:
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://github.com/Parallel-NetCDF/PnetCDF")
    assert(repositoryLocation.getOwner() == "Parallel-NetCDF")
    assert(repositoryLocation.getRepositoryName() == "PnetCDF")


def test_RepositoryLocation_canParseOwnerAndNameOfOfficialGitlabRepository() -> None:
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://gitlab.com/exaalt/parsplice")
    assert(repositoryLocation.getOwner() == "exaalt")
    assert(repositoryLocation.getRepositoryName() == "parsplice")


def test_RepositoryLocation_canParseOwnerAndNameOfSelfHostedGitlabRepository() -> None:
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://xgitlab.cels.anl.gov/darshan/darshancode")
    assert(repositoryLocation.getOwner() == "darshan")
    assert(repositoryLocation.getRepositoryName() == "darshancode")


def test_RepositoryLocation_canParseOwnerAndNameOfOfficialBitbucketRepository() -> None:
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://bitbucket.org/berkeleylab/picsar")
    assert(repositoryLocation.getOwner() == "berkeleylab")
    assert(repositoryLocation.getRepositoryName() == "picsar")


def test_RepositoryLocation_canParseOwnerAndNameOfSelfHostedBitbucketRepository() -> None:
    repositoryLocation = gitEntities.RepositoryLocation(
        url="bitbucket.snl.gov/project/repo")
    assert(repositoryLocation.getOwner() == "project")
    assert(repositoryLocation.getRepositoryName() == "repo")


def test_RepositoryLocation_canParseOwnerAndNameOfUnknownRepository() -> None:
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://code-int.ornl.gov/exnihilo/Exnihilo")
    assert(repositoryLocation.getOwner() == "exnihilo")
    assert(repositoryLocation.getRepositoryName() == "Exnihilo")


def test_RepositoryLocation_AllOrNothingForPartialMatchesOnOwnerAndRepo() -> None:
    repositoryLocationA = gitEntities.RepositoryLocation(
        url="https://github.com/Parallel-NetCDF/")
    assert(repositoryLocationA.getOwner() is None)
    assert(repositoryLocationA.getRepositoryName() is None)

    repositoryLocationB = gitEntities.RepositoryLocation(
        url="https://gitlab.com/exaalt")
    assert(repositoryLocationB.getOwner() is None)
    assert(repositoryLocationB.getRepositoryName() is None)

    repositoryLocationC = gitEntities.RepositoryLocation(
        url="https://xgitlab.cels.anl.gov/darshan/")
    assert(repositoryLocationC.getOwner() is None)
    assert(repositoryLocationC.getRepositoryName() is None)

    repositoryLocationD = gitEntities.RepositoryLocation(
        url="https://bitbucket.org/berkeleylab/")
    assert(repositoryLocationD.getOwner() is None)
    assert(repositoryLocationD.getRepositoryName() is None)

    repositoryLocationE = gitEntities.RepositoryLocation(
        url="https://bitbucket.hdfgroup.org/hdffv/")
    assert(repositoryLocationE.getOwner() is None)
    assert(repositoryLocationE.getRepositoryName() is None)

    repositoryLocationE = gitEntities.RepositoryLocation(
        url="https://code-int.ornl.gov/")
    assert(repositoryLocationE.getOwner() is None)
    assert(repositoryLocationE.getRepositoryName() is None)


def test_VersionControlPlatformCredentials_isConstructibleByFactory() -> None:
    factory = gitEntities.GitEntityFactory()
    credentials = factory.createVersionControlPlatformCredentials(
        username="name", password="password", token="token")


def test_VersionControlPlatformCredentials_isDirectlyConstructible() -> None:
    credentials = gitEntities.VersionControlPlatformCredentials(
        username="name", password="password", token="token")


def test_VersionControlPlatformCredentials_canStoreCredentialValues() -> None:
    credentials = gitEntities.VersionControlPlatformCredentials(
        username="name", password="password", token="token")
    assert(credentials.getUsername() == "name")
    assert(credentials.getPassword() == "password")
    assert(credentials.getToken() == "token")


def test_VersionControlPlatformCredentials_allowsUsernameAndPasswordComboInConstructor() -> None:
    credentials = gitEntities.VersionControlPlatformCredentials(
        username="name", password="password")
    assert(credentials.hasUsernameAndPasswordAvailable())
    assert(not credentials.hasTokenAvailable())


def test_VersionControlPlatformCredentials_allowsJustTokenInConstructor() -> None:
    credentials = gitEntities.VersionControlPlatformCredentials(token="token")
    assert(not credentials.hasUsernameAndPasswordAvailable())
    assert(credentials.hasTokenAvailable())


def test_VersionControlPlatformCredentials_allDefaultParametersInConstructorIsError() -> None:
    with pytest.raises(ValueError):
        credentials = gitEntities.VersionControlPlatformCredentials()


def test_VersionControlPlatformCredentials_providingOnlyUsernameWithoutPasswordOrViceVersaIsError() -> None:
    with pytest.raises(ValueError):
        credentials = gitEntities.VersionControlPlatformCredentials(username="name")
    with pytest.raises(ValueError):
        credentials = gitEntities.VersionControlPlatformCredentials(password="password")


def test_CredentialKeychain_canConstructEmptyKeychain() -> None:
    keychain = gitEntities.CredentialKeychain(credentialsDictionary={})


def test_CredentialKeychain_anEmptyKeychainHasLengthOfZero() -> None:
    keychain = gitEntities.CredentialKeychain(credentialsDictionary={})
    assert(len(keychain) == 0)


def test_CredentialKeychain_canStoreValidCredentials() -> None:
    credentialsDictionary = {}
    entry = {"url": "https://github.com/", "token": "ab341m32"}
    credentialsDictionary["githubplatform"] = entry
    keychain = gitEntities.CredentialKeychain(
        credentialsDictionary=credentialsDictionary)
    assert(len(keychain) == 1)


def test_CredentialKeychain_credentialsMustBeInDictionary() -> None:
    credentialsDictionary: List[int] = []
    with pytest.raises(TypeError):
        keychain = gitEntities.CredentialKeychain(
            credentialsDictionary=credentialsDictionary)  # type: ignore


def test_CredentialKeychain_thereCanOnlyBeOneCredentialObjectForEachUniqueURL() -> None:
    credentialsDictionary = {}
    entryA = {"url": "https://github.com/", "token": "ab341m32"}
    entryB = {"url": "https://github.com/", "token": "cak13113"}
    credentialsDictionary["githubplatform"] = entryA
    credentialsDictionary["alternative"] = entryB
    keychain = gitEntities.CredentialKeychain(
        credentialsDictionary=credentialsDictionary)
    assert(len(keychain) == 1)


def test_CredentialKeychain_canMatchRepositoryLocationWithCredentials() -> None:
    credentialsDictionary = {}
    entry = {"url": "https://github.com/", "token": "ab341m32"}
    credentialsDictionary["githubplatform"] = entry
    keychain = gitEntities.CredentialKeychain(
        credentialsDictionary=credentialsDictionary)

    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://github.com/Parallel-NetCDF/PnetCDF")

    lookupResult = keychain.lookup(repositoryLocation)
    assert(lookupResult is not None)
    assert(isinstance(lookupResult, gitEntities.VersionControlPlatformCredentials))
    assert(lookupResult.hasTokenAvailable())
    assert(lookupResult.getToken() == "ab341m32")


def test_CredentialKeychain_canFailToFindCredentials() -> None:
    credentialsDictionary = {}
    entry = {"url": "https://github.com/", "token": "ab341m32"}
    credentialsDictionary["githubplatform"] = entry
    keychain = gitEntities.CredentialKeychain(
        credentialsDictionary=credentialsDictionary)

    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://xgitlab.cels.anl.gov/darshan/darshancode")

    lookupResult = keychain.lookup(repositoryLocation)
    assert(lookupResult is None)


def test_CredentialKeychain_ifMultipleEntriesMatchLongestIsChosen() -> None:
    credentialsDictionary = {}
    entryA = {"url": "https://github.com/", "token": "ab341m32"}
    entryB = {"url": "https://github.com/Parallel-NetCDF", "token": "q198krq13"}
    entryC = {"url": "https://github.com/Parallel-NetCDF/PnetCDF", "token": "14l1mn8a"}
    entryD = {
        "url": "https://bitbucket.hdfgroup.org/scm/hdffv/hdf5",
        "token": "iual1334"}
    credentialsDictionary["platform"] = entryA
    credentialsDictionary["project"] = entryB
    credentialsDictionary["repository"] = entryC
    credentialsDictionary["unrelated"] = entryD
    keychain = gitEntities.CredentialKeychain(
        credentialsDictionary=credentialsDictionary)

    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://github.com/Parallel-NetCDF/PnetCDF")

    lookupResult = keychain.lookup(repositoryLocation)
    assert(lookupResult is not None)
    assert(lookupResult.getToken() == "14l1mn8a")


def test_GitHubAPISessionCreator_isConstructibleByFactory() -> None:
    factory = gitEntities.GitEntityFactory()
    githubCreator = factory.createGitHubAPISessionCreator()


def test_GitHubAPISessionCreator_isDirectlyConstructible() -> None:
    githubCreator = gitEntities.GitHubAPISessionCreator()


def test_GitHubAPISessionCreator_canHandleAppropriateRepository() -> None:
    githubCreator = gitEntities.GitHubAPISessionCreator()
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://github.com/Parallel-NetCDF/PnetCDF")
    assert(githubCreator.canHandleRepository(repositoryLocation))


def test_GitHubAPISessionCreator_rejectsInappropriateRepositories() -> None:
    githubCreator = gitEntities.GitHubAPISessionCreator()
    repositoryLocationGitlab = gitEntities.RepositoryLocation(
        url="https://gitlab.com/exaalt/parsplice")
    repositoryLocationBitbucket = gitEntities.RepositoryLocation(
        url="https://bitbucket.org/berkeleylab/picsar")
    repositoryLocationGarbage = gitEntities.RepositoryLocation(url="garbage")
    assert(not githubCreator.canHandleRepository(repositoryLocationGitlab))
    assert(not githubCreator.canHandleRepository(repositoryLocationBitbucket))
    assert(not githubCreator.canHandleRepository(repositoryLocationGarbage))


def test_VCSAPISessionCompositeCreator_isConstructibleByFactory() -> None:
    factory = gitEntities.GitEntityFactory()
    githubCreator = factory.createVCSAPISessionCompositeCreator()


def test_VCSAPISessionCompositeCreator_isDirectlyConstructible() -> None:
    compositeCreator = gitEntities.VCSAPISessionCompositeCreator()


def test_VCSAPISessionCompositeCreator_InitiallyHasNoChildren() -> None:
    compositeCreator = gitEntities.VCSAPISessionCompositeCreator()
    assert (compositeCreator.getNumberOfChildren() == 0)


def test_VCSAPISessionCompositeCreator_CantFulfillRequestsWithoutChildren() -> None:
    compositeCreator = gitEntities.VCSAPISessionCompositeCreator()
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://github.com/Parallel-NetCDF/PnetCDF")
    assert (compositeCreator.canHandleRepository(repositoryLocation) == False)


def test_VCSAPISessionCompositeCreator_CanStoreChildren() -> None:
    compositeCreator = gitEntities.VCSAPISessionCompositeCreator()
    githubCreator = gitEntities.GitHubAPISessionCreator()
    compositeCreator.addChild(githubCreator)
    assert(compositeCreator.hasChild(githubCreator))
    assert(compositeCreator.getNumberOfChildren() == 1)


def test_VCSAPISessionCompositeCreator_CanRemoveChildren() -> None:
    compositeCreator = gitEntities.VCSAPISessionCompositeCreator()
    githubCreator = gitEntities.GitHubAPISessionCreator()
    compositeCreator.addChild(githubCreator)
    compositeCreator.removeChild(githubCreator)
    assert(not compositeCreator.hasChild(githubCreator))


def test_VCSAPISessionCompositeCreator_CanFulfillRequestIfChildCan() -> None:
    compositeCreator = gitEntities.VCSAPISessionCompositeCreator()
    githubCreator = gitEntities.GitHubAPISessionCreator()
    compositeCreator.addChild(githubCreator)
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://github.com/Parallel-NetCDF/PnetCDF")
    assert(compositeCreator.canHandleRepository(repositoryLocation))


def test_VCSAPISessionCompositeCreator_CanFulfillRequestIfChildCant() -> None:
    compositeCreator = gitEntities.VCSAPISessionCompositeCreator()
    githubCreator = gitEntities.GitHubAPISessionCreator()
    compositeCreator.addChild(githubCreator)
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://gitlab.com/exaalt/parsplice")
    assert(not compositeCreator.canHandleRepository(repositoryLocation))


def test_GitlabAPISessionCreator_isConstructibleByFactory() -> None:
    factory = gitEntities.GitEntityFactory()
    githubCreator = factory.createGitlabAPISessionCreator()


def test_GitlabAPISessionCreator_isDirectlyConstructible() -> None:
    gitlabCreator = gitEntities.GitlabAPISessionCreator()


def test_GitlabAPISessionCreator_canHandleAppropriateRepository() -> None:
    gitlabCreator = gitEntities.GitlabAPISessionCreator()
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://gitlab.com/exaalt/parsplice")
    assert(gitlabCreator.canHandleRepository(repositoryLocation))


def test_GitlabAPISessionCreator_rejectsInappropriateRepositories() -> None:
    gitlabCreator = gitEntities.GitlabAPISessionCreator()
    repositoryLocationGitlab = gitEntities.RepositoryLocation(
        url="https://github.com/Parallel-NetCDF/PnetCDF")
    repositoryLocationBitbucket = gitEntities.RepositoryLocation(
        url="https://bitbucket.org/berkeleylab/picsar")
    repositoryLocationGarbage = gitEntities.RepositoryLocation(url="garbage")
    assert(not gitlabCreator.canHandleRepository(repositoryLocationGitlab))
    assert(not gitlabCreator.canHandleRepository(repositoryLocationBitbucket))
    assert(not gitlabCreator.canHandleRepository(repositoryLocationGarbage))


def test_GitlabAPISessionCreator_usernameAndPasswordComboWillTriggerRuntimeError() -> None:
    gitlabCreator = gitEntities.GitlabAPISessionCreator()
    repositoryLocation = gitEntities.RepositoryLocation(
        url="https://gitlab.com/repo/owner")
    credentials = gitEntities.VersionControlPlatformCredentials(
        username="name", password="password", token=None)
    with pytest.raises(RuntimeError):
        gitlabCreator.connect(repositoryLocation, credentials)
