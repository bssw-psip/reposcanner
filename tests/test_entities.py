import pytest
import reposcanner.git as gitEntities

def test_RepositoryLocation_isConstructibleByFactory():
        factory = gitEntities.GitEntityFactory()
        repositoryLocation = factory.createRepositoryLocation(url="github.com/owner/repository")

def test_RepositoryLocation_isDirectlyConstructible():
        repositoryLocation = gitEntities.RepositoryLocation(url="github.com/owner/repository")
        
def test_RepositoryLocation_canStoreURL():
        url = "arbitrary.edu/repo/name"
        repositoryLocation = gitEntities.RepositoryLocation(url="arbitrary.edu/repo/name")
        assert(repositoryLocation.getURL() == url) 
        
def test_RepositoryLocation_canIdentifyGitHubURLs():
        repositoryLocation = gitEntities.RepositoryLocation(url="https://github.com/Parallel-NetCDF/PnetCDF")
        assert(repositoryLocation.getVersionControlPlatform() == gitEntities.RepositoryLocation.VersionControlPlatform.GITHUB)
        assert(repositoryLocation.getVersionControlHostType() == gitEntities.RepositoryLocation.HostType.OFFICIAL)
        
def test_RepositoryLocation_canIdentifyGitlabURLs():
        repositoryLocationOfficial = gitEntities.RepositoryLocation(url="https://gitlab.com/exaalt/parsplice")
        assert(repositoryLocationOfficial.getVersionControlPlatform() == gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)
        assert(repositoryLocationOfficial.getVersionControlHostType() == gitEntities.RepositoryLocation.HostType.OFFICIAL)
        
        repositoryLocationSelfHosted = gitEntities.RepositoryLocation(url="https://xgitlab.cels.anl.gov/darshan/darshan")
        assert(repositoryLocationSelfHosted.getVersionControlPlatform() == gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)
        assert(repositoryLocationSelfHosted.getVersionControlHostType() == gitEntities.RepositoryLocation.HostType.SELFHOSTED)
        
def test_RepositoryLocation_canIdentifyBitbucketURLs():
        repositoryLocationOfficial = gitEntities.RepositoryLocation(url="https://bitbucket.org/berkeleylab/picsar")
        assert(repositoryLocationOfficial.getVersionControlPlatform() == gitEntities.RepositoryLocation.VersionControlPlatform.BITBUCKET)
        assert(repositoryLocationOfficial.getVersionControlHostType() == gitEntities.RepositoryLocation.HostType.OFFICIAL)
        
        repositoryLocationSelfHosted = gitEntities.RepositoryLocation(url="https://bitbucket.hdfgroup.org/scm/hdffv/hdf5")
        assert(repositoryLocationSelfHosted.getVersionControlPlatform() == gitEntities.RepositoryLocation.VersionControlPlatform.BITBUCKET)
        assert(repositoryLocationSelfHosted.getVersionControlHostType() == gitEntities.RepositoryLocation.HostType.SELFHOSTED)
        
def test_RepositoryLocation_unrecognizedURLsAreUnknown():
        repositoryLocationA = gitEntities.RepositoryLocation(url="http://flash.uchicago.edu/site/flashcode/coderequest/")
        assert(repositoryLocationA.getVersionControlPlatform() == gitEntities.RepositoryLocation.VersionControlPlatform.UNKNOWN)
        assert(repositoryLocationA.getVersionControlHostType() == gitEntities.RepositoryLocation.HostType.UNKNOWN)
        
        repositoryLocationB = gitEntities.RepositoryLocation(url="https://code-int.ornl.gov/exnihilo/Exnihilo")
        assert(repositoryLocationB.getVersionControlPlatform() == gitEntities.RepositoryLocation.VersionControlPlatform.UNKNOWN)
        assert(repositoryLocationB.getVersionControlHostType() == gitEntities.RepositoryLocation.HostType.UNKNOWN)
        
def test_RepositoryLocation_expectedPlatformOverridesActualPlatform():
        repositoryLocationA = gitEntities.RepositoryLocation(url="https://code-int.ornl.gov/exnihilo/Exnihilo",
                expectedPlatform=gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)
        assert(repositoryLocationA.getVersionControlPlatform() == gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)
        
        repositoryLocationB = gitEntities.RepositoryLocation(url="https://github.com/Parallel-NetCDF/PnetCDF",
                expectedPlatform=gitEntities.RepositoryLocation.VersionControlPlatform.BITBUCKET)
        assert(repositoryLocationB.getVersionControlPlatform() == gitEntities.RepositoryLocation.VersionControlPlatform.BITBUCKET)
        
def test_RepositoryLocation_providingPlatformButNotHostTypeMakesItUnknown():
        repositoryLocation = gitEntities.RepositoryLocation(url="https://code-int.ornl.gov/exnihilo/Exnihilo",
                expectedPlatform=gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)
        assert(repositoryLocation.getVersionControlHostType() == gitEntities.RepositoryLocation.HostType.UNKNOWN)
        
def test_RepositoryLocation_providingBothPlatformAndHostTypeRespectsBothChoices():
        repositoryLocation = gitEntities.RepositoryLocation(url="https://code-int.ornl.gov/exnihilo/Exnihilo",
                expectedPlatform=gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB,
                expectedHostType=gitEntities.RepositoryLocation.HostType.SELFHOSTED)
        assert(repositoryLocation.getVersionControlPlatform() == gitEntities.RepositoryLocation.VersionControlPlatform.GITLAB)     
        assert(repositoryLocation.getVersionControlHostType() == gitEntities.RepositoryLocation.HostType.SELFHOSTED)
        
def test_RepositoryLocation_providingBothOwnerAndRepositoryNameRespectsBothChoices():
        repositoryLocation = gitEntities.RepositoryLocation(url="https://bitbucket.hdfgroup.org/scm/hdffv/hdf5",
                expectedOwner="hdffv",
                expectedRepositoryName="hdf5")
        assert(repositoryLocation.getOwner() == "hdffv")     
        assert(repositoryLocation.getRepositoryName() == "hdf5")
        
def test_RepositoryLocation_canParseOwnerAndNameOfGitHubRepository():
        repositoryLocation = gitEntities.RepositoryLocation(url="https://github.com/Parallel-NetCDF/PnetCDF")
        assert(repositoryLocation.getOwner() == "Parallel-NetCDF")     
        assert(repositoryLocation.getRepositoryName() == "PnetCDF")
        
def test_RepositoryLocation_canParseOwnerAndNameOfOfficialGitlabRepository():
        repositoryLocation = gitEntities.RepositoryLocation(url="https://gitlab.com/exaalt/parsplice")
        assert(repositoryLocation.getOwner() == "exaalt")     
        assert(repositoryLocation.getRepositoryName() == "parsplice")
        
def test_RepositoryLocation_canParseOwnerAndNameOfSelfHostedGitlabRepository():
        repositoryLocation = gitEntities.RepositoryLocation(url="https://xgitlab.cels.anl.gov/darshan/darshancode")
        assert(repositoryLocation.getOwner() == "darshan")     
        assert(repositoryLocation.getRepositoryName() == "darshancode")
        
def test_RepositoryLocation_canParseOwnerAndNameOfOfficialBitbucketRepository():
        repositoryLocation = gitEntities.RepositoryLocation(url="https://bitbucket.org/berkeleylab/picsar")
        assert(repositoryLocation.getOwner() == "berkeleylab")     
        assert(repositoryLocation.getRepositoryName() == "picsar")
        
def test_RepositoryLocation_canParseOwnerAndNameOfSelfHostedBitbucketRepository():
        repositoryLocation = gitEntities.RepositoryLocation(url="bitbucket.snl.gov/project/repo")
        assert(repositoryLocation.getOwner() == "project")     
        assert(repositoryLocation.getRepositoryName() == "repo")
        
def test_RepositoryLocation_canParseOwnerAndNameOfUnknownRepository():
        repositoryLocation = gitEntities.RepositoryLocation(url="https://code-int.ornl.gov/exnihilo/Exnihilo")
        assert(repositoryLocation.getOwner() == "exnihilo")     
        assert(repositoryLocation.getRepositoryName() == "Exnihilo")
        
def test_RepositoryLocation_AllOrNothingForPartialMatchesOnOwnerAndRepo():
        repositoryLocationA = gitEntities.RepositoryLocation(url="https://github.com/Parallel-NetCDF/")
        assert(repositoryLocationA.getOwner() == None)
        assert(repositoryLocationA.getRepositoryName() == None)
        
        repositoryLocationB = gitEntities.RepositoryLocation(url="https://gitlab.com/exaalt")
        assert(repositoryLocationB.getOwner() == None)
        assert(repositoryLocationB.getRepositoryName() == None)
        
        repositoryLocationC = gitEntities.RepositoryLocation(url="https://xgitlab.cels.anl.gov/darshan/")
        assert(repositoryLocationC.getOwner() == None)
        assert(repositoryLocationC.getRepositoryName() == None)
        
        repositoryLocationD = gitEntities.RepositoryLocation(url="https://bitbucket.org/berkeleylab/")
        assert(repositoryLocationD.getOwner() == None)
        assert(repositoryLocationD.getRepositoryName() == None)
        
        repositoryLocationE = gitEntities.RepositoryLocation(url="https://bitbucket.hdfgroup.org/hdffv/")
        assert(repositoryLocationE.getOwner() == None)
        assert(repositoryLocationE.getRepositoryName() == None)
        
        repositoryLocationE = gitEntities.RepositoryLocation(url="https://code-int.ornl.gov/")
        assert(repositoryLocationE.getOwner() == None)
        assert(repositoryLocationE.getRepositoryName() == None)
        
def test_VersionControlPlatformCredentials_isConstructibleByFactory():
        factory = gitEntities.GitEntityFactory()
        credentials = factory.createVersionControlPlatformCredentials(username="name",password="password",token="token")

def test_VersionControlPlatformCredentials_isDirectlyConstructible():
        credentials = gitEntities.VersionControlPlatformCredentials(username="name",password="password",token="token")
        
def test_VersionControlPlatformCredentials_canStoreCredentialValues():
        credentials = gitEntities.VersionControlPlatformCredentials(username="name",password="password",token="token")
        assert(credentials.getUsername() == "name")
        assert(credentials.getPassword() == "password")
        assert(credentials.getToken() == "token")
        
def test_VersionControlPlatformCredentials_allowsUsernameAndPasswordComboInConstructor():
        credentials = gitEntities.VersionControlPlatformCredentials(username="name",password="password")
        assert(credentials.hasUsernameAndPasswordAvailable())
        assert(not credentials.hasTokenAvailable())
        
def test_VersionControlPlatformCredentials_allowsJustTokenInConstructor():
        credentials = gitEntities.VersionControlPlatformCredentials(token="token")
        assert(not credentials.hasUsernameAndPasswordAvailable())
        assert(credentials.hasTokenAvailable())
        
def test_VersionControlPlatformCredentials_allDefaultParametersInConstructorIsError():
        with pytest.raises(ValueError):
                credentials = gitEntities.VersionControlPlatformCredentials()
                
def test_VersionControlPlatformCredentials_providingOnlyUsernameWithoutPasswordOrViceVersaIsError():
        with pytest.raises(ValueError):
                credentials = gitEntities.VersionControlPlatformCredentials(username="name")
        with pytest.raises(ValueError):
                credentials = gitEntities.VersionControlPlatformCredentials(password="password")
        
        
        
        
        
        
        
        
        