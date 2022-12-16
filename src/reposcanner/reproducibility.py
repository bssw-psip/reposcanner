from reposcanner.routines import OfflineRepositoryRoutine
from reposcanner.requests import OfflineRoutineRequest
from reposcanner.response import ResponseFactory
import os, json, copy


class ReproducibilityOfflineRoutineRequest(OfflineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, workspaceDirectory):
        super().__init__(repositoryURL, outputDirectory, workspaceDirectory)

class ReproducibilityOfflineRoutine(OfflineRepositoryRoutine):
    """
    This offline routine will clone a given workflow, then will analyze the source 
    code that the workflow runs. It will output a data file with metrics regarding
    the source code.
    """
    modules = []

    def getRequestType(self):
            return ReproducibilityOfflineRoutineRequest

    def offlineImplementation(self, request, session):
        response = self.findModuleList(request.getCloneDirectory())
        if not response.wasSuccessful():
            return response
        modules = response.getAttachments()[0]
        print("AFTER")
        print(modules)




        responseFactory = ResponseFactory()
        return responseFactory.createFailureResponse(
            message="ReproducibilityOfflineRoutine is incomplete")

    def findModuleList(self, repository):
        response = ResponseFactory()
        modulesFile = repository / 'modules.json'
        if os.path.exists(modulesFile):
            file = open(str(modulesFile))
            modulesJson = json.load(file)
            modules = modulesJson["repos"]["nf-core/modules"]["modules"]
            return response.createSuccessResponse(
                attachments=[copy.deepcopy(modules)]
            )
        else:
            return response.createFailureResponse(
                message = "No module list found in workflow"
            )

    def parseModuleList(self, modules):
        return