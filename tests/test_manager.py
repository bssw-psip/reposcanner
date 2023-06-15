import reposcanner.manager as management
import reposcanner.requests as requests
import reposcanner.data as data
import pathlib
import pytest


def test_ManagerRepositoryRoutineTask_isDirectlyConstructible() -> None:
    task = management.ManagerRepositoryRoutineTask(
        projectID="PROJID",
        projectName="SciKit",
        url="https://github.com/scikit/scikit/",
        request=requests.RepositoryRoutineRequestModel(
            repositoryURL="https://github.com/scikit/scikit/",
            outputDirectory="./"))


def test_ManagerRepositoryRoutineTask_isConstructibleByFactory() -> None:
    factory = management.TaskFactory()
    task = factory.createManagerRepositoryRoutineTask(
        projectID="PROJID",
        projectName="SciKit",
        url="https://github.com/scikit/scikit/",
        request=requests.RepositoryRoutineRequestModel(
            repositoryURL="https://github.com/scikit/scikit/",
            outputDirectory="./"))


def test_ManagerAnalysisTask_isDirectlyConstructible() -> None:
    task = management.ManagerAnalysisTask(request=requests.AnalysisRequestModel())


def test_ManagerAnalysisTask_isConstructibleByFactory() -> None:
    factory = management.TaskFactory()
    task = factory.createManagerAnalysisTask(request=requests.AnalysisRequestModel())


def test_ReposcannerManager_isDirectlyConstructible() -> None:
    args = type('', (), {})()
    args.outputDirectory = "./"
    args.workspaceDirectory = "./"
    args.gui = True
    manager = management.ReposcannerManager(
        notebook=None,
        outputDirectory=args.outputDirectory,
        workspaceDirectory=args.workspaceDirectory,
        gui=args.gui)


def test_ReposcannerManager_GUIModeIsDisabledByDefault() -> None:
    manager = management.ReposcannerManager(notebook=None)
    assert(not manager.isGUIModeEnabled())


def test_ReposcannerManager_GUIModeCanBeEnabledAtConstructionTime() -> None:
    manager = management.ReposcannerManager(
        notebook=None,
        gui=True)
    assert(manager.isGUIModeEnabled())


def test_ReposcannerManager_initiallyHasNoRoutinesOrAnalyses() -> None:
    manager = management.ReposcannerManager(
        notebook=None,
        gui=True)
    assert(len(manager.getRoutines()) == 0)
    assert(len(manager.getAnalyses()) == 0)


def test_ReposcannerManager_CanParseConfigYAMLFileAndConstructRoutines(tmp_path: pathlib.Path) -> None:
    manager = management.ReposcannerManager(
        notebook=None,
        gui=True)
    filePath = tmp_path / "config.yaml"

    with open(filePath, 'w') as outfile:
        contents = """
                routines:
                  - ContributorAccountListRoutine
                  - reposcanner.contrib:ContributorAccountListRoutine
                analyses:
                  - GambitCommitAuthorshipInferenceAnalysis
                  - reposcanner.contrib:GambitCommitAuthorshipInferenceAnalysis
                """
        outfile.write(contents)

    configEntity = data.YAMLData(filePath)
    configEntity.readFromFile()
    configDict = configEntity.getData()

    with pytest.deprecated_call():
        manager.initializeRoutinesAndAnalyses(configDict)
    routines = manager.getRoutines()
    assert(len(routines) == 2)
    assert(routines[0].__class__.__name__ == "ContributorAccountListRoutine")
    assert(routines[1].__class__.__name__ == "ContributorAccountListRoutine")
    analyses = manager.getAnalyses()
    assert(len(analyses) == 2)
    assert(analyses[0].__class__.__name__ == "GambitCommitAuthorshipInferenceAnalysis")
    assert(analyses[1].__class__.__name__ == "GambitCommitAuthorshipInferenceAnalysis")


def test_ReposcannerManager_missingRoutinesInConfigCausesValueError(tmp_path: pathlib.Path) -> None:
    manager = management.ReposcannerManager(
        notebook=None,
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
    with pytest.raises(ValueError), pytest.deprecated_call():
        manager.initializeRoutinesAndAnalyses(configDict)
