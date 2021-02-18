import pytest
import reposcanner.requests as requests
from reposcanner.git import CredentialKeychain


def test_AnalysisRequestModel_isDirectlyConstructible():
        analysisRequest = requests.AnalysisRequestModel()

def test_AnalysisRequestModel_isAnAnalysisRequestType():
        analysisRequest = requests.AnalysisRequestModel()
        assert(analysisRequest.isAnalysisRequestType())
        assert(not analysisRequest.isRoutineRequestType())

def test_AnalysisRequestModel_hasNoErrorsByDefault():
        analysisRequest = requests.AnalysisRequestModel()
        assert(not analysisRequest.hasErrors())

def test_AnalysisRequestModel_defaultDataCriteriaAcceptsLiterallyEverything():
        analysisRequest = requests.AnalysisRequestModel()
        assert(analysisRequest.getDataCriteria() == analysisRequest.criteriaFunction)
        assert(analysisRequest.criteriaFunction("garbage") is True)
        assert(analysisRequest.criteriaFunction(42) is True)
        assert(analysisRequest.criteriaFunction(analysisRequest) is True)

def test_RoutineRequestModel_isDirectlyConstructible():
        requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        
def test_AnalysisRequestModel_isARoutineRequestType():
        routineRequest = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        assert(not routineRequest.isAnalysisRequestType())
        assert(routineRequest.isRoutineRequestType())
        
def test_RoutineRequestModel_hasNoErrorsForValidInput():
        request = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        assert(not request.hasErrors())
        
def test_RoutineRequestModel_canGenerateAndStoreRepositoryLocation():
        request = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        location = request.getRepositoryLocation()
        assert(location != None)
        assert(location.isRecognizable())
        assert(location.getOwner() == "owner")
        assert(location.getRepositoryName() == "repo")
        
        
def test_RoutineRequestModel_badURLMeansError():
        requestA = requests.RoutineRequestModel(repositoryURL="garbage",outputDirectory="./")
        assert(requestA.hasErrors())
        
        requestB = requests.RoutineRequestModel(repositoryURL="https://unrecognizedhost.org/owner/repo",outputDirectory="./")
        assert(requestB.hasErrors())
        
        requestC = requests.RoutineRequestModel(repositoryURL=None,outputDirectory="./")
        assert(requestC.hasErrors())

def test_RoutineRequestModel_canStoreOutputDirectory():
        request = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./")
        assert(request.getOutputDirectory() == "./")
        
def test_RoutineRequestModel_badOutputDirectoryMeansError():
        requestA = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory=None)
        assert(requestA.hasErrors())
        
        requestB = requests.RoutineRequestModel(repositoryURL="https://github.com/owner/repo",outputDirectory="./nonexistent/directory/")
        assert(requestB.hasErrors())
        
def test_OnlineRoutineRequest_isDirectlyConstructible():
        requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                token = "ab5571mc1") 

def test_OnlineRoutineRequest_canPassKeychainToConstructor():
        credentialsDictionary = {}
        entry = {"url" : "https://github.com/", "token": "ab341m32"}
        credentialsDictionary["platform"] = entry
        keychain = CredentialKeychain(credentialsDictionary=credentialsDictionary)
        requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                keychain = keychain)
        
def test_OnlineRoutineRequest_canStoreValidCredentials():
        requestA = requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                token = "ab5571mc1") 
        assert(not requestA.hasErrors())
        credentialsA = requestA.getCredentials()
        assert(credentialsA.hasTokenAvailable())
        assert(credentialsA.getToken() == "ab5571mc1")
        
        requestB = requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                username = "argyle",
                password = "luggage") 
        assert(not requestB.hasErrors())
        credentialsB = requestB.getCredentials()
        assert(credentialsB.hasUsernameAndPasswordAvailable())
        assert(credentialsB.getUsername() == "argyle")
        assert(credentialsB.getPassword() == "luggage")
        
def test_OnlineRoutineRequest_canStoreValidCredentialsViaKeychain():
        credentialsDictionary = {}
        entry = {"url" : "https://github.com/", "token": "ab341m32"}
        credentialsDictionary["platform"] = entry
        
        keychain = CredentialKeychain(credentialsDictionary=credentialsDictionary)
        request = requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                keychain = keychain)
        assert(not request.hasErrors())
        credentials = request.getCredentials()
        assert(credentials.hasTokenAvailable())
        assert(credentials.getToken() == "ab341m32")
         
def test_OnlineRoutineRequest_keychainTakesPrecedenceOverOtherInputs():
        credentialsDictionary = {}
        entry = {"url" : "https://github.com/", "token": "ab341m32"}
        credentialsDictionary["platform"] = entry
        
        keychain = CredentialKeychain(credentialsDictionary=credentialsDictionary)
        request = requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                token = "qq4132c",
                keychain = keychain)
        assert(not request.hasErrors())
        credentials = request.getCredentials()
        assert(credentials.hasTokenAvailable())
        assert(credentials.getToken() == "ab341m32")
        
def test_OnlineRoutineRequest_doesNotSwitchToOtherCredentialsIfKeychainLacksThem():
        credentialsDictionary = {}
        entry = {"url" : "https://gitlab.com/", "token": "ab341m32"}
        credentialsDictionary["platform"] = entry
        
        keychain = CredentialKeychain(credentialsDictionary=credentialsDictionary)
        request = requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                token = "qq4132c",
                keychain = keychain)
        assert(request.hasErrors())
        
def test_OnlineRoutineRequest_badCredentialsMeansError():
        requestA = requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                token = None)
        assert(requestA.hasErrors())
        
        requestB = requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                username = "argyle",
                password = None)
        assert(requestB.hasErrors())
        
        requestC = requests.OnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                username = None,
                password = "luggage")
        assert(requestC.hasErrors())
        
def test_OfflineRoutineRequest_isDirectlyConstructible():
        requests.OfflineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                workspaceDirectory="./")
                
def test_OfflineRoutineRequest_canStoreValidWorkspaceDirectory():
        request = requests.OfflineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                workspaceDirectory="./")
        assert(not request.hasErrors())
        assert(request.getWorkspaceDirectory() == "./")
        
def test_OnlineRoutineRequest_badWorkspaceDirectoryMeansError():
        requestA = requests.OfflineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                workspaceDirectory = None)
        assert(requestA.hasErrors())
        
        requestB = requests.OfflineRoutineRequest(repositoryURL="https://github.com/owner/repo",
                outputDirectory="./",
                workspaceDirectory = "./nonexistent/directory")
        assert(requestB.hasErrors())
        
        
        
        
        