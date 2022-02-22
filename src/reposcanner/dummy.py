"""
Here we have do-nothing dummy routines and analyses used in integration testing for Reposcanner.
"""
from reposcanner.routines import OfflineRepositoryRoutine,OnlineRepositoryRoutine
from reposcanner.analyses import DataAnalysis
from reposcanner.requests import OfflineRoutineRequest,OnlineRoutineRequest,AnalysisRequestModel
from reposcanner.response import ResponseFactory
from reposcanner.provenance import ReposcannerRunInformant
from reposcanner.data import DataEntityFactory
import datetime

class DummyOfflineRoutineRequest(OfflineRoutineRequest):
	def __init__(self,repositoryURL,outputDirectory,workspaceDirectory):
		super().__init__(repositoryURL,outputDirectory,workspaceDirectory)
				
class DummyOfflineRoutine(OfflineRepositoryRoutine):
	"""
	This offline routine will clone a given repository, then will output a data
	file that only contains metadata.
	"""

	def getRequestType(self):
		return DummyOfflineRoutineRequest
	
	def offlineImplementation(self,request,session):
		factory = DataEntityFactory()
		output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_dummyOfflineData.csv".format(
			outputDirectory=request.getOutputDirectory(),
			repoName=request.getRepositoryLocation().getRepositoryName()))
		output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
		output.setCreator(self.__class__.__name__)
		output.setDateCreated(datetime.date.today())
		output.setURL(request.getRepositoryLocation().getURL())
		output.writeToFile()
		responseFactory = ResponseFactory()
		return responseFactory.createSuccessResponse(message="DummyOfflineRoutine completed!",attachments=output)

		
class DummyOnlineRoutineRequest(OnlineRoutineRequest):
        def __init__(self,repositoryURL,outputDirectory,username=None,password=None,token=None,keychain=None):
                super().__init__(repositoryURL,outputDirectory,username=username,password=password,token=token,keychain=keychain)
		
class DummyOnlineRoutine(OnlineRepositoryRoutine):
	"""
	This offline routine will establish an online API session with the given
	repository, then will output a data file that only contains metadata.
	"""
	def getRequestType(self):
		return DummyOnlineRoutineRequest
		
	def githubImplementation(self,request,session):
		factory = DataEntityFactory()
		output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_dummyOnlineData.csv".format(
			outputDirectory=request.getOutputDirectory(),
			repoName=request.getRepositoryLocation().getRepositoryName()))
		output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
		output.setCreator(self.__class__.__name__)
		output.setDateCreated(datetime.date.today())
		output.setURL(request.getRepositoryLocation().getURL())
		output.writeToFile()
		responseFactory = ResponseFactory()
		return responseFactory.createSuccessResponse(message="DummyOnlineRoutine completed!",attachments=output)
	
	def gitlabImplementation(self,request,session):
		factory = DataEntityFactory()
		output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_dummyOnlineData.csv".format(
			outputDirectory=request.getOutputDirectory(),
			repoName=request.getRepositoryLocation().getRepositoryName()))
		output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
		output.setCreator(self.__class__.__name__)
		output.setDateCreated(datetime.date.today())
		output.setURL(request.getRepositoryLocation().getURL())
		output.writeToFile()
		responseFactory = ResponseFactory()
		return responseFactory.createSuccessResponse(message="DummyOnlineRoutine completed!",attachments=output)
		
class DummyAnalysisRequest(AnalysisRequestModel):
	def criteriaFunction(self,entity):
		"""
		The DummyAnalysisRequest attempts to fetch all data from the data store which
		was created by a DummyOfflineRoutine or a DummyOnlineRoutine.
		"""
		try:
			creator = entity.getCreator()
			if creator == "DummyOfflineRoutine" or creator == "DummyOnlineRoutine":
				return True
			else:
				return False
		except AttributeError as e:
			return False

class DummyAnalysis(DataAnalysis):
	def getRequestType(self):
		return DummyAnalysisRequest
	def execute(self,request):
		responseFactory = ResponseFactory()
		return responseFactory.createSuccessResponse(message="DummyAnalysis completed!")
