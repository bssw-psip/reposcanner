import reposcanner.dummy as dummy
import reposcanner.provenance as provenance
import reposcanner.requests
import reposcanner.data as data
from reposcanner.manager import ReposcannerManager
import pytest

def test_DummyOfflineRoutineRequest_isDirectlyConstructible():
        request = dummy.DummyOfflineRoutineRequest(repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        workspaceDirectory = "./")

def test_DummyOfflineRoutine_isDirectlyConstructible():
        routine = dummy.DummyOfflineRoutine()

def test_DummyOfflineRoutine_hasMatchingRequestType():
        routine = dummy.DummyOfflineRoutine()
        assert(routine.getRequestType() == dummy.DummyOfflineRoutineRequest )

def test_DummyOfflineRoutine_canHandleAppropriateRequest():
		request = dummy.DummyOfflineRoutineRequest(repositoryURL="https://github.com/owner/repo",
			outputDirectory="./",
			workspaceDirectory = "./")
		routine = dummy.DummyOfflineRoutine()
		assert(not request.hasErrors())
		assert(routine.canHandleRequest(request))

def test_DummyOfflineRoutine_willRejectInAppropriateRequest():
		request = reposcanner.requests.BaseRequestModel()
		routine = dummy.DummyOfflineRoutine()
		assert(not isinstance(request, routine.getRequestType()))
		print(routine.getRequestType())
		print(type(request))
		assert(not routine.canHandleRequest(request))

def test_DummyOnlineRoutineRequest_isDirectlyConstructible():
        request = dummy.DummyOnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
        outputDirectory="./",
        token = "ab5571mc1")

def test_DummyOnlineRoutine_isDirectlyConstructible():
        routine = dummy.DummyOnlineRoutine()

def test_DummyOnlineRoutine_hasMatchingRequestType():
        routine = dummy.DummyOnlineRoutine()
        assert(routine.getRequestType() == dummy.DummyOnlineRoutineRequest )

def test_DummyOnlineRoutine_canHandleAppropriateRequest():
		request = dummy.DummyOnlineRoutineRequest(repositoryURL="https://github.com/owner/repo",
			outputDirectory="./",
			token = "ab5571mc1")
		routine = dummy.DummyOnlineRoutine()
		assert(not request.hasErrors())
		assert(routine.canHandleRequest(request))

def test_DummyOnlineRoutine_willRejectInAppropriateRequest():
		request = reposcanner.requests.BaseRequestModel()
		routine = dummy.DummyOnlineRoutine()
		assert(not isinstance(request, routine.getRequestType()))
		print(routine.getRequestType())
		print(type(request))
		assert(not routine.canHandleRequest(request))

def test_DummyAnalysisRequest_isDirectlyConstructible():
		request = dummy.DummyAnalysisRequest()


def test_DummyAnalysisRequest_criteriaFunctionExpectsDummyRoutineData():
		request = dummy.DummyAnalysisRequest()
		dataEntityFactory = data.DataEntityFactory()
		offlineData = dataEntityFactory.createAnnotatedCSVData("data/examplerepo_dummyOfflineRoutine.csv")
		offlineData.setCreator(dummy.DummyOfflineRoutine().__class__.__name__)
		assert(offlineData.getCreator() == "DummyOfflineRoutine")
		onlineData = dataEntityFactory.createAnnotatedCSVData("data/examplerepo_dummyOnlineRoutine.csv")
		onlineData.setCreator(dummy.DummyOnlineRoutine().__class__.__name__)
		assert(onlineData.getCreator() == "DummyOnlineRoutine")

		assert(request.criteriaFunction(offlineData) is True)
		assert(request.criteriaFunction(onlineData) is True)
		assert(request.criteriaFunction("garbage") is False)


def test_DummyAnalysisRequest_canFetchDataFromStore():
		store = data.DataEntityStore()
		dataEntityFactory = data.DataEntityFactory()
		offlineData = dataEntityFactory.createAnnotatedCSVData("data/examplerepo_dummyOfflineRoutine.csv")
		offlineData.setCreator(dummy.DummyOfflineRoutine().__class__.__name__)
		store.insert(offlineData)
		onlineData = dataEntityFactory.createAnnotatedCSVData("data/examplerepo_dummyOnlineRoutine.csv")
		onlineData.setCreator(dummy.DummyOnlineRoutine().__class__.__name__)
		store.insert(onlineData)

		request = dummy.DummyAnalysisRequest()
		request.fetchDataFromStore(store)
		fetchedData = request.getData()
		assert(len(fetchedData) == 2)

def test_DummyAnalysis_isDirectlyConstructible():
		analysis = dummy.DummyAnalysis()

def test_DummyAnalysis_canHandleAppropriateRequest():
		analysis = dummy.DummyAnalysis()
		assert(analysis.getRequestType() == dummy.DummyAnalysisRequest)
		request = dummy.DummyAnalysisRequest()
		assert(analysis.canHandleRequest(request))

def test_canCompleteDummyWorkflow():
	dataEntityFactory = data.DataEntityFactory()
	#Imitate passing command-line arguments.
	args = type('', (), {})()
	args.repositories = "tests/dummyWorkflowFiles/repositories.yml"
	args.credentials = "tests/dummyWorkflowFiles/credentials.yml"
	args.config = "tests/dummyWorkflowFiles/config.yml"
	args.notebookOutputPath = "tests/dummyWorkflowFiles/"
	args.outputDirectory = "./"
	args.workspaceDirectory = "./"

	repositoriesDataFile = dataEntityFactory.createYAMLData(args.repositories)
	credentialsDataFile = dataEntityFactory.createYAMLData(args.credentials)
	configDataFile = dataEntityFactory.createYAMLData(args.config)

	repositoriesDataFile.readFromFile()
	credentialsDataFile.readFromFile()
	configDataFile.readFromFile()

	credentialsData = credentialsDataFile.getData()
	if credentialsData["GitHubPlatformCredentials"]["token"] == "SECRET":
		pytest.skip("Not running on GitHub, so credentials are not available")

	notebook = provenance.ReposcannerLabNotebook(args.notebookOutputPath)

	notebook.onStartup(args)

	manager = ReposcannerManager(notebook=notebook,outputDirectory=args.outputDirectory,workspaceDirectory=args.workspaceDirectory,gui=False)

	manager.run(repositoriesDataFile,credentialsDataFile,configDataFile)

	notebook.onExit()
	notebook.publishNotebook()
