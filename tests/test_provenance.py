import pytest
import datetime
import reposcanner.provenance as provenance
import reposcanner.contrib as contributionRoutines
import reposcanner.manager as manager
import reposcanner.response as responses
import reposcanner.data as dataEntities


def test_ReposcannerRunInformant_isDirectlyConstructible():
    informant = provenance.ReposcannerRunInformant()


def test_ReposcannerRunInformant_differentInstancesProvideTheSameExecutionID():
    informantA = provenance.ReposcannerRunInformant()
    informantB = provenance.ReposcannerRunInformant()

    executionIDA = informantA.getReposcannerExecutionID()
    executionIDB = informantB.getReposcannerExecutionID()

    assert(executionIDA == executionIDB)


def test_ReposcannerRunInformant_differentInstancesProvideTheSameVersionInfo():
    informantA = provenance.ReposcannerRunInformant()
    informantB = provenance.ReposcannerRunInformant()

    versionInfoA = informantA.getReposcannerVersion()
    versionInfoB = informantB.getReposcannerVersion()

    assert(versionInfoA == versionInfoB)


def test_ReposcannerLabNotebook_isDirectlyConstructible():
    notebook = provenance.ReposcannerLabNotebook(notebookOutputDirectory="./")


def test_ReposcannerLabNotebook_canLogArgsOnStartup():
    notebook = provenance.ReposcannerLabNotebook(notebookOutputDirectory="./")
    args = type('', (), {})()
    args.repositories = "repositories.yaml"
    args.credentials = "credentials.yaml"
    args.config = "config.yaml"
    notebook.onStartup(args)
    jsonDocument = notebook.getJSONRepresentation()

    assert('agent' in jsonDocument)
    assert('rs:ReposcannerManager' in jsonDocument['agent'])

    assert(jsonDocument['entity']['rs:repositories']['rs:path'] == 'repositories.yaml')
    assert(jsonDocument['entity']['rs:credentials']['rs:path'] == 'credentials.yaml')
    assert(jsonDocument['entity']['rs:config']['rs:path'] == 'config.yaml')


def test_ReposcannerLabNotebook_canLogCreatedRoutines():
    routine = contributionRoutines.ContributorAccountListRoutine()
    notebook = provenance.ReposcannerLabNotebook(notebookOutputDirectory="./")
    notebook.onRoutineCreation(routine)
    jsonDocument = notebook.getJSONRepresentation()
    assert("rs:ContributorAccountListRoutine" in jsonDocument['agent'])
    relationExistsBetweenManagerAndRoutine = False
    for relationID in jsonDocument['actedOnBehalfOf']:
        relation = jsonDocument['actedOnBehalfOf'][relationID]
        if relation['prov:delegate'] == 'rs:ContributorAccountListRoutine' and relation['prov:responsible'] == 'rs:ReposcannerManager':
            relationExistsBetweenManagerAndRoutine = True
    assert(relationExistsBetweenManagerAndRoutine)


def test_ReposcannerLabNotebook_canLogCreatedAnalyses():
    # TODO: We need to define what analyses are before we can deal with logging them.
    pass


def test_ReposcannerLabNotebook_canLogCreatedTasks():
    request = contributionRoutines.ContributorAccountListRoutineRequest(
        repositoryURL="https://github.com/scikit/scikit", outputDirectory="./", token="ab5571mc1")
    task = manager.ManagerRepositoryRoutineTask(
        projectID="PROJID",
        projectName="SciKit",
        url="https://github.com/scikit/scikit",
        request=request)

    notebook = provenance.ReposcannerLabNotebook(notebookOutputDirectory="./")
    notebook.onTaskCreation(task)
    jsonDocument = notebook.getJSONRepresentation()

    activityID = list(jsonDocument['activity'].keys())[0]

    activity = jsonDocument['activity'][activityID]
    assert(activity['rs:projectID'] == 'PROJID')
    assert(activity['rs:projectName'] == 'SciKit')
    assert(activity['rs:URL'] == 'https://github.com/scikit/scikit')

    relationExistsBetweenManagerAndTask = False
    for relationID in jsonDocument['wasGeneratedBy']:
        relation = jsonDocument['wasGeneratedBy'][relationID]
        if relation['prov:entity'] == 'rs:ReposcannerManager' and relation['prov:activity'] == activityID:
            relationExistsBetweenManagerAndTask = True
    assert(relationExistsBetweenManagerAndTask)


def test_ReposcannerLabNotebook_canLogStartOfTask():

    notebook = provenance.ReposcannerLabNotebook(notebookOutputDirectory="./")

    request = contributionRoutines.ContributorAccountListRoutineRequest(
        repositoryURL="https://github.com/scikit/scikit", outputDirectory="./", token="ab5571mc1")
    task = manager.ManagerRepositoryRoutineTask(
        projectID="PROJID",
        projectName="SciKit",
        url="https://github.com/scikit/scikit",
        request=request)
    notebook.onTaskCreation(task)

    routine = contributionRoutines.ContributorAccountListRoutine()
    notebook.onRoutineCreation(routine)

    notebook.onTaskStart(task, dataEntities.DataEntityStore(), routine)

    jsonDocument = notebook.getJSONRepresentation()

    activityID = list(jsonDocument['activity'].keys())[0]

    relationExistsBetweenRoutineAndTask = False
    for relationID in jsonDocument['wasStartedBy']:
        relation = jsonDocument['wasStartedBy'][relationID]
        if relation['prov:activity'] == activityID and relation['prov:trigger'] == 'rs:ContributorAccountListRoutine':
            assert('prov:time' in relation)
            relationExistsBetweenRoutineAndTask = True
    assert(relationExistsBetweenRoutineAndTask)

    print(jsonDocument)


def test_ReposcannerLabNotebook_canLogCompletionOfTask(tmpdir):
    # Overwriting methods of ContributorAccountListRoutine to return a
    # predetermined response.

    def generateCSVDataFile(tmpdir):
        informant = provenance.ReposcannerRunInformant()
        dataEntity = dataEntities.AnnotatedCSVData("loggedentitytest.csv")
        timestamp = datetime.date.today()

        columnNames = ["Login Name", "Actual Name", "Email(s)"]
        columnDatatypes = ["str", "str", "str"]

        dataEntity.setReposcannerExecutionID(informant.getReposcannerExecutionID())
        dataEntity.setCreator("ContributorAccountListRoutine")
        dataEntity.setDateCreated(timestamp)
        dataEntity.setProjectID("PROJID")
        dataEntity.setProjectName("SciKit")
        dataEntity.setURL("https://github.com/scikit/scikit")
        dataEntity.setColumnNames(columnNames)
        dataEntity.setColumnDatatypes(columnDatatypes)

        dataEntity.addRecord(["johnsmith", "John Smith", "jsmith@gmail.com"])
        dataEntity.addRecord(["alicejones", "Alice Jones", "alice@llnl.gov"])
        dataEntity.writeToFile()

    generateCSVDataFile(tmpdir)

    def executeGeneratesResponse(self, request):
        factory = responses.ResponseFactory()
        response = factory.createSuccessResponse(attachments=[])
        factory = dataEntities.DataEntityFactory()
        csvDataEntity = factory.createAnnotatedCSVData(filePath="loggedentitytest.csv")
        csvDataEntity.readFromFile()
        response.addAttachment(csvDataEntity)
        return response

    contributionRoutines.ContributorAccountListRoutine.execute = executeGeneratesResponse

    notebook = provenance.ReposcannerLabNotebook(notebookOutputDirectory="./")

    request = contributionRoutines.ContributorAccountListRoutineRequest(
        repositoryURL="https://github.com/scikit/scikit", outputDirectory="./", token="ab5571mc1")
    task = manager.ManagerRepositoryRoutineTask(
        projectID="PROJID",
        projectName="SciKit",
        url="https://github.com/scikit/scikit",
        request=request)

    routine = contributionRoutines.ContributorAccountListRoutine()

    notebook.onTaskCreation(task)
    notebook.onRoutineCreation(routine)

    task.process(
        agents=[routine],
        store=dataEntities.DataEntityStore(),
        notebook=notebook)

    jsonDocument = notebook.getJSONRepresentation()
    taskID = list(jsonDocument['activity'].keys())[0]

    relationExistsBetweenRoutineAndTask = False
    for relationID in jsonDocument['wasEndedBy']:
        relation = jsonDocument['wasEndedBy'][relationID]
        if relation['prov:activity'] == taskID and relation['prov:trigger'] == 'rs:ContributorAccountListRoutine':
            relationExistsBetweenRoutineAndTask = True
    assert(relationExistsBetweenRoutineAndTask)

    dataEntityID = None
    for entityID in jsonDocument['entity']:
        dataEntity = jsonDocument['entity'][entityID]
        if dataEntity['rs:path'] == 'loggedentitytest.csv':
            dataEntityID = entityID
    assert(dataEntityID is not None)

    relationExistsBetweenTaskAndFile = False
    for relationID in jsonDocument['wasGeneratedBy']:
        relation = jsonDocument['wasGeneratedBy'][relationID]
        if relation['prov:entity'] == dataEntityID and relation['prov:activity'] == taskID:
            relationExistsBetweenTaskAndFile = True
    assert(relationExistsBetweenTaskAndFile)


def test_ReposcannerLabNotebook_canLogNonstandardDataDuringCompletionOfTask(tmpdir):
    def executeGeneratesResponse(self, request):
        factory = responses.ResponseFactory()
        response = factory.createSuccessResponse(attachments=[])
        factory = dataEntities.DataEntityFactory()
        nonstandardData = {"a": 5, "b": 255}
        response.addAttachment(nonstandardData)
        return response

    contributionRoutines.ContributorAccountListRoutine.execute = executeGeneratesResponse

    notebook = provenance.ReposcannerLabNotebook(notebookOutputDirectory="./")

    request = contributionRoutines.ContributorAccountListRoutineRequest(
        repositoryURL="https://github.com/scikit/scikit", outputDirectory="./", token="ab5571mc1")
    task = manager.ManagerRepositoryRoutineTask(
        projectID="PROJID",
        projectName="SciKit",
        url="https://github.com/scikit/scikit",
        request=request)

    routine = contributionRoutines.ContributorAccountListRoutine()

    notebook.onTaskCreation(task)
    notebook.onRoutineCreation(routine)

    task.process(
        agents=[routine],
        store=dataEntities.DataEntityStore(),
        notebook=notebook)

    jsonDocument = notebook.getJSONRepresentation()
    taskID = list(jsonDocument['activity'].keys())[0]

    dataEntityID = None
    for entityID in jsonDocument['entity']:
        dataEntity = jsonDocument['entity'][entityID]
        if dataEntity['rs:dataType'] == 'dict':
            dataEntityID = entityID
    assert(dataEntityID is not None)

    relationExistsBetweenTaskAndFile = False
    for relationID in jsonDocument['wasGeneratedBy']:
        relation = jsonDocument['wasGeneratedBy'][relationID]
        if relation['prov:entity'] == dataEntityID and relation['prov:activity'] == taskID:
            relationExistsBetweenTaskAndFile = True
    assert(relationExistsBetweenTaskAndFile)


def test_ReposcannerLabNotebook_canPublishResults(tmpdir):

    def generateCSVDataFile():
        informant = provenance.ReposcannerRunInformant()
        dataEntity = dataEntities.AnnotatedCSVData("loggedentitytest.csv")
        timestamp = datetime.date.today()

        columnNames = ["Login Name", "Actual Name", "Email(s)"]
        columnDatatypes = ["str", "str", "str"]

        dataEntity.setReposcannerExecutionID(informant.getReposcannerExecutionID())
        dataEntity.setCreator("ContributorAccountListRoutine")
        dataEntity.setDateCreated(timestamp)
        dataEntity.setProjectID("PROJID")
        dataEntity.setProjectName("SciKit")
        dataEntity.setURL("https://github.com/scikit/scikit")
        dataEntity.setColumnNames(columnNames)
        dataEntity.setColumnDatatypes(columnDatatypes)

        dataEntity.addRecord(["johnsmith", "John Smith", "jsmith@gmail.com"])
        dataEntity.addRecord(["alicejones", "Alice Jones", "alice@llnl.gov"])
        dataEntity.writeToFile()

    generateCSVDataFile()

    def executeGeneratesResponse(self, request):
        factory = responses.ResponseFactory()
        response = factory.createSuccessResponse(attachments=[])
        return response

    def exportAddsAnAttachment(self, request, response):
        factory = dataEntities.DataEntityFactory()
        csvDataEntity = factory.createAnnotatedCSVData(filePath="loggedentitytest.csv")
        csvDataEntity.readFromFile()
        response.addAttachment(csvDataEntity)
    contributionRoutines.ContributorAccountListRoutine.execute = executeGeneratesResponse
    contributionRoutines.ContributorAccountListRoutine.export = exportAddsAnAttachment

    outputDir = tmpdir.mkdir("notebookOutput/")
    notebook = provenance.ReposcannerLabNotebook(notebookOutputDirectory=outputDir)

    request = contributionRoutines.ContributorAccountListRoutineRequest(
        repositoryURL="https://github.com/scikit/scikit", outputDirectory="./", token="ab5571mc1")
    task = manager.ManagerRepositoryRoutineTask(
        projectID="PROJID",
        projectName="SciKit",
        url="https://github.com/scikit/scikit",
        request=request)

    routine = contributionRoutines.ContributorAccountListRoutine()

    notebook.onTaskCreation(task)
    notebook.onRoutineCreation(routine)

    task.process(
        agents=[routine],
        store=dataEntities.DataEntityStore(),
        notebook=notebook)

    notebook.publishNotebook()
