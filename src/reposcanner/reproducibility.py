from reposcanner.routines import OfflineRepositoryRoutine
from reposcanner.requests import OfflineRoutineRequest
from reposcanner.response import ResponseFactory
from reposcanner.data import DataEntityFactory
from reposcanner.provenance import ReposcannerRunInformant
import os, datetime, fnmatch


class ReproducibilityOfflineRoutineRequest(OfflineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, workspaceDirectory):
        super().__init__(repositoryURL, outputDirectory, workspaceDirectory)

class ReproducibilityOfflineRoutine(OfflineRepositoryRoutine):
    """
    This offline routine will clone a given workflow, then will analyze the source 
    code that the workflow runs. It will output a data file with metrics regarding
    the source code.
    """

    def getRequestType(self):
            return ReproducibilityOfflineRoutineRequest

    def resetClassVariables(self):
        self.num_nfcore_modules = 0
        self.nfcore_modules = ["nf-core Modules"]
        self.num_local_modules = 0
        self.local_modules = ["local Modules"]
        self.num_local_subworkflows = 0
        self.local_subworkflows = ["local Subworkflows"]
        self.num_nfcore_subworkflows = 0
        self.nfcore_subworkflows = ["nf-core Subworkflows"]
        self.num_workflows = 0
        self.workflows = ["Workflows"]
        self.workflows_num_lines = {}

    def offlineImplementation(self, request, session):
        self.resetClassVariables()
        self.findNfCoreModuleList(request.getCloneDirectory())
        self.findLocalModules(request.getCloneDirectory())
        self.findLocalSubworkflows(request.getCloneDirectory())
        self.findNfCoreSubworkflows(request.getCloneDirectory())
        self.findWorkflows(request.getCloneDirectory())
        self.parseWorkflows(request.getCloneDirectory())
        return self.generateResponse(request)

    def generateResponse(self, request):
        #Metadata
        factory = DataEntityFactory()
        output = factory.createAnnotatedCSVData(
            "{outputDirectory}/{repoName}_reproducibilityData.csv".format(
                outputDirectory=request.getOutputDirectory(),
                repoName=request.getRepositoryLocation().getRepositoryName()))
        output.setReposcannerExecutionID(
            ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(self.__class__.__name__)
        output.setDateCreated(datetime.date.today())
        output.setURL(request.getRepositoryLocation().getURL())

        #Real Data
        output.addRecord(["num nf-core modules", self.num_nfcore_modules])
        output.addRecord(self.nfcore_modules)
        output.addRecord(["num local modules", self.num_local_modules])
        output.addRecord(self.local_modules)
        output.addRecord(["num nf-core subworkflows", self.num_nfcore_subworkflows])
        output.addRecord(self.nfcore_subworkflows)
        output.addRecord(["num local subworkflows", self.num_local_subworkflows])
        output.addRecord(self.local_subworkflows)
        output.addRecord(["num workflows", self.num_workflows])
        output.addRecord(self.workflows)

        index = 1
        while index <= len(self.workflows) - 1:
            self.workflows_num_lines[self.workflows[index]]
            output.addRecord([self.workflows[index] + " number of lines", self.workflows_num_lines[self.workflows[index]]])
            index += 1

        #Write output
        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(
            message="DummyOfflineRoutine completed!", attachments=output)

    def findNfCoreModuleList(self, repository):
        ModulesPath = repository / "modules" / "nf-core"
        if os.path.exists(ModulesPath):
            for root, dirnames, filenames in os.walk(ModulesPath):
                for filename in fnmatch.filter(filenames, '*.nf'):
                    newRoot = root.replace(str(ModulesPath), "")
                    self.nfcore_modules.append(os.path.join(newRoot, filename))
            self.num_nfcore_modules = len(self.nfcore_modules) - 1

    def findLocalModules(self, repository):
        localModulesPath = repository / "modules" / "local"
        if os.path.exists(localModulesPath):
            for root, dirnames, filenames in os.walk(localModulesPath):
                for filename in fnmatch.filter(filenames, '*.nf'):
                    newRoot = root.replace(str(localModulesPath), "")
                    self.local_modules.append(os.path.join(newRoot, filename))
            self.num_local_modules = len(self.local_modules) - 1

    def findLocalSubworkflows(self, repository):
        localSubworkflowsPath = repository / "subworkflows" / "local"
        if os.path.exists(localSubworkflowsPath):
            for root, dirnames, filenames in os.walk(localSubworkflowsPath):
                for filename in fnmatch.filter(filenames, '*.nf'):
                    newRoot = root.replace(str(localSubworkflowsPath), "")
                    self.local_subworkflows.append(os.path.join(newRoot, filename))
            self.num_local_subworkflows = len(self.local_subworkflows) - 1

    def findNfCoreSubworkflows(self, repository):
        nfcoreSubworkflowsPath = repository / "subworkflows" / "nf-core"
        if os.path.exists(nfcoreSubworkflowsPath):
            for root, dirnames, filenames in os.walk(nfcoreSubworkflowsPath):
                for filename in fnmatch.filter(filenames, '*.nf'):
                    newRoot = root.replace(str(nfcoreSubworkflowsPath), "")
                    self.nfcore_subworkflows.append(os.path.join(newRoot, filename))
            self.num_nfcore_subworkflows = len(self.nfcore_subworkflows) - 1

    def findWorkflows(self, repository):
        workflowsPath = repository / "workflows"
        if os.path.exists(workflowsPath):
            for root, dirnames, filenames in os.walk(workflowsPath):
                for filename in fnmatch.filter(filenames, "*.nf"):
                    newRoot = root.replace(str(workflowsPath), "")
                    self.workflows.append(os.path.join(newRoot, filename))
            self.num_workflows = len(self.workflows) - 1

    def parseWorkflows(self, repository):
        for workflow in self.workflows:
            file = repository / "workflows" / workflow
            if os.path.exists(file):
                numLines = 0
                with open(file) as fp:
                    for line in fp:
                        if line.strip():
                            numLines +=1
                self.workflows_num_lines.update({workflow: numLines})

