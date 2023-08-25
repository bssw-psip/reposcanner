import reposcanner.manager as management
import reposcanner.requests as requests
import reposcanner.data as data
import pytest


def test_ManagerRepositoryRoutineTask_isDirectlyConstructible():
    task = management.ManagerRepositoryRoutineTask(
        projectID="PROJID",
        projectName="SciKit",
        url="https://github.com/scikit/scikit/",
        request=requests.RepositoryRoutineRequestModel(
            repositoryURL="https://github.com/scikit/scikit/",
            outputDirectory="./"))


def test_ManagerRepositoryRoutineTask_isConstructibleByFactory():
    factory = management.TaskFactory()
    task = factory.createManagerRepositoryRoutineTask(
        projectID="PROJID",
        projectName="SciKit",
        url="https://github.com/scikit/scikit/",
        request=requests.RepositoryRoutineRequestModel(
            repositoryURL="https://github.com/scikit/scikit/",
            outputDirectory="./"))


def test_ManagerAnalysisTask_isDirectlyConstructible():
    task = management.ManagerAnalysisTask(request=requests.AnalysisRequestModel())


def test_ManagerAnalysisTask_isConstructibleByFactory():
    factory = management.TaskFactory()
    task = factory.createManagerAnalysisTask(request=requests.AnalysisRequestModel())


def test_ReposcannerManager_isDirectlyConstructible():
    args = type('', (), {})()
    args.outputDirectory = "./"
    args.workspaceDirectory = "./"
    args.gui = True
    manager = management.ReposcannerManager(
        notebook=None,
        outputDirectory=args.outputDirectory,
        workspaceDirectory=args.workspaceDirectory,
        gui=args.gui)


def test_ReposcannerManager_GUIModeIsDisabledByDefault():
    manager = management.ReposcannerManager(
        notebook=None, outputDirectory=None, workspaceDirectory=None)
    assert(not manager.isGUIModeEnabled())


def test_ReposcannerManager_GUIModeCanBeEnabledAtConstructionTime():
    manager = management.ReposcannerManager(
        notebook=None,
        outputDirectory=None,
        workspaceDirectory=None,
        gui=True)
    assert(manager.isGUIModeEnabled())


def test_ReposcannerManager_initiallyHasNoRoutinesOrAnalyses():
    manager = management.ReposcannerManager(
        notebook=None,
        outputDirectory=None,
        workspaceDirectory=None,
        gui=True)
    assert(len(manager.getRoutines()) == 0)
    assert(len(manager.getAnalyses()) == 0)


def test_ReposcannerManager_CanParseConfigYAMLFileAndConstructRoutines(tmp_path):
    manager = management.ReposcannerManager(
        notebook=None,
        outputDirectory=None,
        workspaceDirectory=None,
        gui=True)
    filePath = tmp_path / "config.yaml"

    with open(filePath, 'w') as outfile:
        contents = """
                routines:
                  - ContributorAccountListRoutine
                """
        outfile.write(contents)

    configEntity = data.YAMLData(filePath)
    configEntity.readFromFile()
    configDict = configEntity.getData()

    manager.initializeRoutinesAndAnalyses(configDict)
    routines = manager.getRoutines()
    assert(len(routines) == 1)
    assert(routines[0].__class__.__name__ == "ContributorAccountListRoutine")


def test_ReposcannerManager_missingRoutinesInConfigCausesValueError(tmp_path):
    manager = management.ReposcannerManager(
        notebook=None,
        outputDirectory=None,
        workspaceDirectory=None,
        gui=True)
    filePath = tmp_path / "config.yaml"

    with open(filePath, 'w') as outfile:
        contents = """
                routines:
                  - ContributorAccountListRoutine
                  - NonexistentRoutine
                """
        outfile.write(contents)

    configEntity = data.YAMLData(filePath)
    configEntity.readFromFile()
    configDict = configEntity.getData()

    # Attempting to find and initialize NonexistentRoutine will trigger a ValueError.
    with pytest.raises(ValueError):
        manager.initializeRoutinesAndAnalyses(configDict)
