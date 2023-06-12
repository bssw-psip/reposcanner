from reposcanner.routines import OfflineRepositoryRoutine
from reposcanner.requests import OfflineRoutineRequest
from reposcanner.response import ResponseFactory
from reposcanner.data import DataEntityFactory
from reposcanner.provenance import ReposcannerRunInformant
from pathlib import Path
import os, datetime, fnmatch, re, shutil
from pygit2 import GIT_BRANCH_ALL


class NextflowReproducibilityOfflineRoutineRequest(OfflineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, workspaceDirectory):
        super().__init__(repositoryURL, outputDirectory, workspaceDirectory)

class NextflowDataStruct:
    def __init__(self, tagName):
        self.tagName = str(tagName)
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

class NextflowReproducibilityOfflineRoutine(OfflineRepositoryRoutine):
    """
    This offline routine will clone a given Nextflow workflow, then will analyze the source
    code that the workflow runs. It will output a data file with metrics regarding
    the source code.
    """

    def getRequestType(self):
            return NextflowReproducibilityOfflineRoutineRequest

    def resetClassVariables(self):
        self.tags = []
        self.data = []

    def deleteRepository(self, request):
        shutil.rmtree(request.getCloneDirectory())

    def offlineImplementation(self, request, session):
        self.resetClassVariables()

        self.getTags(request, session)
        print(self.tags)

        # Analyze default branch
        dataStruct = NextflowDataStruct(session.head.shorthand)
        self.findNfCoreModuleList(request.getCloneDirectory(), dataStruct)
        self.findLocalModules(request.getCloneDirectory(), dataStruct)
        self.findLocalSubworkflows(request.getCloneDirectory(), dataStruct)
        self.findNfCoreSubworkflows(request.getCloneDirectory(), dataStruct)
        self.findWorkflows(request.getCloneDirectory(), dataStruct)
        self.parseWorkflows(request.getCloneDirectory(), dataStruct)

        self.data.append(dataStruct)

        # Analyze tagged branches
        for tag in self.tags:
            dataStruct = NextflowDataStruct(tag)

            print("checking out " + request.getRepositoryLocation().getRepositoryName() + " with the tag " + tag)
            session.checkout(tag)

            self.findNfCoreModuleList(request.getCloneDirectory(), dataStruct)
            self.findLocalModules(request.getCloneDirectory(), dataStruct)
            self.findLocalSubworkflows(request.getCloneDirectory(), dataStruct)
            self.findNfCoreSubworkflows(request.getCloneDirectory(), dataStruct)
            self.findWorkflows(request.getCloneDirectory(), dataStruct)
            self.parseWorkflows(request.getCloneDirectory(), dataStruct)

            self.data.append(dataStruct)

        return self.generateResponse(request)

    def getTags(self, request, session):
        regex = re.compile('^refs/tags/')

        self.tags = [r for r in session.references if regex.match(r)]

        return

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
        for tag in self.data:
            output.addRecord([tag.tagName])
            output.addRecord(["num nf-core modules", tag.num_nfcore_modules])
            output.addRecord(tag.nfcore_modules)
            output.addRecord(["num local modules", tag.num_local_modules])
            output.addRecord(tag.local_modules)
            output.addRecord(["num nf-core subworkflows", tag.num_nfcore_subworkflows])
            output.addRecord(tag.nfcore_subworkflows)
            output.addRecord(["num local subworkflows", tag.num_local_subworkflows])
            output.addRecord(tag.local_subworkflows)
            output.addRecord(["num workflows", tag.num_workflows])
            output.addRecord(tag.workflows)

            index = 1
            while index <= len(tag.workflows) - 1:
                tag.workflows_num_lines[tag.workflows[index]]
                output.addRecord([tag.workflows[index] + " number of lines", tag.workflows_num_lines[tag.workflows[index]]])
                index += 1

        self.deleteRepository(request)

        #Write output
        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(
            message="completed!", attachments=output)

    def findNfCoreModuleList(self, repository, dataStruct):
        ModulesPath = repository / "modules" / "nf-core"
        if os.path.exists(ModulesPath):
            for root, dirnames, filenames in os.walk(ModulesPath):
                for filename in fnmatch.filter(filenames, '*.nf'):
                    newRoot = root.replace(str(ModulesPath), "")
                    dataStruct.nfcore_modules.append(os.path.join(newRoot, filename))
            dataStruct.num_nfcore_modules = len(dataStruct.nfcore_modules) - 1

    def findLocalModules(self, repository, dataStruct):
        localModulesPath = repository / "modules" / "local"
        if os.path.exists(localModulesPath):
            for root, dirnames, filenames in os.walk(localModulesPath):
                for filename in fnmatch.filter(filenames, '*.nf'):
                    newRoot = root.replace(str(localModulesPath), "")
                    dataStruct.local_modules.append(os.path.join(newRoot, filename))
            dataStruct.num_local_modules = len(dataStruct.local_modules) - 1

    def findLocalSubworkflows(self, repository, dataStruct):
        localSubworkflowsPath = repository / "subworkflows" / "local"
        if os.path.exists(localSubworkflowsPath):
            for root, dirnames, filenames in os.walk(localSubworkflowsPath):
                for filename in fnmatch.filter(filenames, '*.nf'):
                    newRoot = root.replace(str(localSubworkflowsPath), "")
                    dataStruct.local_subworkflows.append(os.path.join(newRoot, filename))
            dataStruct.num_local_subworkflows = len(dataStruct.local_subworkflows) - 1

    def findNfCoreSubworkflows(self, repository, dataStruct):
        nfcoreSubworkflowsPath = repository / "subworkflows" / "nf-core"
        if os.path.exists(nfcoreSubworkflowsPath):
            for root, dirnames, filenames in os.walk(nfcoreSubworkflowsPath):
                for filename in fnmatch.filter(filenames, '*.nf'):
                    newRoot = root.replace(str(nfcoreSubworkflowsPath), "")
                    dataStruct.nfcore_subworkflows.append(os.path.join(newRoot, filename))
            dataStruct.num_nfcore_subworkflows = len(dataStruct.nfcore_subworkflows) - 1

    def findWorkflows(self, repository, dataStruct):
        workflowsPath = repository / "workflows"
        if os.path.exists(workflowsPath):
            for root, dirnames, filenames in os.walk(workflowsPath):
                for filename in fnmatch.filter(filenames, "*.nf"):
                    newRoot = root.replace(str(workflowsPath), "")
                    dataStruct.workflows.append(os.path.join(newRoot, filename))
            dataStruct.num_workflows = len(dataStruct.workflows) - 1

    def parseWorkflows(self, repository, dataStruct):
        for workflow in dataStruct.workflows:
            file = repository / "workflows" / workflow
            if os.path.exists(file):
                numLines = 0
                with open(file) as fp:
                    for line in fp:
                        if line.strip():
                            numLines +=1
                dataStruct.workflows_num_lines.update({workflow: numLines})

class SnakemakeReproducibilityOfflineRoutineRequest(OfflineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, workspaceDirectory):
        super().__init__(repositoryURL, outputDirectory, workspaceDirectory)

class SnakemakeDataStruct:
    def __init__(self, tagName):
        self.tagName = tagName
        self.num_rulesFiles = 0
        self.rulesFiles = ["Snakemake Rule Files"]
        self.rules = {}
        self.num_rules = 0
        self.snakefile_num_lines = 0


class SnakemakeReproducibilityOfflineRoutine(OfflineRepositoryRoutine):
    """
    This offline routine will clone a given Snakemake workflow, then will analyze the source
    code that the workflow runs. It will output a data file with metrics regarding
    the source code.
    """

    def getRequestType(self):
        return SnakemakeReproducibilityOfflineRoutineRequest

    def offlineImplementation(self, request, session):
        self.resetClassVariables()
        self.getTags(session)

        print(self.tags)


        #Analyze default branch
        snakemakeDataStruct = SnakemakeDataStruct(session.head.shorthand)
        self.findRuleFiles(request.getCloneDirectory(), snakemakeDataStruct)
        self.parseSnakefile(request.getCloneDirectory(), snakemakeDataStruct)
        self.data.append(snakemakeDataStruct)


        #Analyze all tags
        for tag in self.tags:
            print("checking out " + request.getRepositoryLocation().getRepositoryName() + " with the tag " + tag)
            session.checkout(tag)

            snakemakeDataStruct = SnakemakeDataStruct(tag)
            self.findRuleFiles(request.getCloneDirectory(), snakemakeDataStruct)
            self.parseSnakefile(request.getCloneDirectory(), snakemakeDataStruct)

            self.data.append(snakemakeDataStruct)

        return self.generateResponse(request)

    def deleteRepository(self, request):
        shutil.rmtree(request.getCloneDirectory())

    def getTags(self, session):
        regex = re.compile('^refs/tags/')
        self.tags = [r for r in session.references if regex.match(r)]
        return

    def resetClassVariables(self):
        self.tags = []
        self.data = []

    def findRuleFiles(self, repository, snakemakeDataStruct):
        rulesPath = repository / "workflow" / "rules"

        if os.path.exists(rulesPath):
            for root, dirnames, filenames in os.walk(rulesPath):
                for filename in fnmatch.filter(filenames, "*.smk"):
                    if filename != "common.smk":
                        snakemakeDataStruct.rulesFiles.append(filename)
                        snakemakeDataStruct.rules[filename] = []
                        self.parseRuleFile(root, filename, snakemakeDataStruct)
            snakemakeDataStruct.num_rulesFiles = len(snakemakeDataStruct.rulesFiles) - 1

    def parseRuleFile(self, dir, file, snakemakeDataStruct):
        fullPath = Path(dir) / file
        if os.path.exists(fullPath):
            numLines = 0
            with open(fullPath) as fp:
                for line in fp:
                    if re.match("rule .+:",line):
                        ruleName = line.split()[1].replace(":","")
                        snakemakeDataStruct.rules[file].append(ruleName)
                        snakemakeDataStruct.num_rules += 1
        return

    def parseSnakefile(self, repository, snakemakeDataStruct):
        snakefile = repository / "workflow" / "Snakefile"

        if os.path.exists(snakefile):
            numLines = 0
            with open(snakefile) as fp:
                for line in fp:
                    if line.strip():
                        numLines += 1
                snakemakeDataStruct.snakefile_num_lines = numLines



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

        for tag in self.data:
            output.addRecord([tag.tagName])

            output.addRecord(["num rule files", tag.num_rulesFiles])
            output.addRecord(tag.rulesFiles)
            output.addRecord(["num rules", tag.num_rules])

            for key in tag.rules:
                record = [key] + tag.rules[key]
                output.addRecord(record)

            output.addRecord(["Snakefile Number of Lines", tag.snakefile_num_lines])


        self.deleteRepository(request)

        #Write output
        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(
            message="completed!", attachments=output)


