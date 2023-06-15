# This future import allows us to reference a class in type annotations before it is declared.
from __future__ import annotations
from reposcanner.git import CredentialKeychain
from reposcanner.data import DataEntityStore, ReposcannerDataEntity, YAMLData
from reposcanner.response import ResponseFactory, ResponseModel
from reposcanner.routines import RepositoryRoutine, ExternalCommandLineToolRoutine, DataMiningRoutine
from reposcanner.requests import BaseRequestModel, AnalysisRequestModel, ExternalCommandLineToolRoutineRequest, RepositoryRoutineRequestModel, OnlineRoutineRequest
from reposcanner.analyses import DataAnalysis
import logging
import warnings
import importlib
import curses
import sys
from typing import Sequence, Union, Optional, List, Iterable, Dict, Any, Tuple, cast, TYPE_CHECKING
from tqdm import tqdm  # For progress checking in non-GUI mode.
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    # TYPE_CHECKING is false when actually executing
    # This avoids an import cycle.
    from reposcanner.provenance import AbstractLabNotebook


class TaskFactory:
    def createManagerRepositoryRoutineTask(
            self,
            projectID: str,
            projectName: str,
            url: str,
            request: RepositoryRoutineRequestModel,
    ) -> ManagerTask:
        return ManagerRepositoryRoutineTask(projectID, projectName, url, request)

    def createManagerExternalCommandLineToolTask(self, request: BaseRequestModel) -> ManagerTask:
        return ManagerExternalCommandLineToolTask(request)

    def createManagerAnalysisTask(self, request: BaseRequestModel) -> ManagerTask:
        return ManagerAnalysisTask(request)


class ManagerTask(ABC):
    """Abstract base class for Task objects. Task objects are simple wrappers around
    requests and responses that makes it easier for the frontend to display execution
    progress."""

    def __init__(self, request: BaseRequestModel) -> None:
        self._request = request
        self._response: Optional[ResponseModel] = None

    def getRequestClassName(self) -> str:
        return self._request.__class__.__name__

    def getRequest(self) -> BaseRequestModel:
        return self._request

    def hasResponse(self) -> bool:
        return self._response is not None

    def getResponse(self) -> ResponseModel:
        assert self._response is not None
        return self._response

    def process(
            self,
            agents: Iterable[Union[DataMiningRoutine, DataAnalysis]],
            store: DataEntityStore,
            notebook: AbstractLabNotebook,
    ) -> None:
        """
        Scan through a set of available routines or analyses and see if any can
        execute the request held by this task. If no routines or analyses can handle
        this request, this method will create a failure response and store it.

        agents: An iterable of RepositoryRoutine and/or DataAnalysis objects.
        store: A DataEntityStore instance, provided by the manager.
        notebook: A ReposcannerNotebook object, used for logging results.
        """
        selectedAgent = None
        for agent in agents:
            if agent.canHandleRequest(self._request):
                selectedAgent = agent
                break
        if selectedAgent is not None:
            if notebook is not None:
                notebook.onTaskStart(self, store, selectedAgent)
            if isinstance(self._request, AnalysisRequestModel):
                self._request.fetchDataFromStore(store)
            self._response = selectedAgent.run(self._request)
            if notebook is not None:
                notebook.onTaskCompletion(self, selectedAgent)
        else:
            responseFactory = ResponseFactory()
            self._response = responseFactory.createFailureResponse(
                message="No routine/analysis was found that could \
                                execute the request ({requestType}).".format(
                    requestType=type(self._request)))

    @abstractmethod
    def getResponseDescription(self) -> str:
        """
        Generate a string that describes the response to the request in a human-readable
        way.
        """
        pass


class ManagerRepositoryRoutineTask(ManagerTask):
    """
    This Task class wraps requests and responses for RepositoryRoutines.
    """

    def __init__(self, projectID: str, projectName: str, url: str, request: RepositoryRoutineRequestModel) -> None:
        super().__init__(request)
        self._projectID = projectID
        self._projectName = projectName
        self._url = url

    def getDescription(self) -> str:
        """
        Generates a string that describes the task.
        """
        if self._projectName is not None and len(self._projectName) > 0:
            nameOrID = self._projectName
        else:
            nameOrID = self._projectID

        assert isinstance(self._request, RepositoryRoutineRequestModel)
        repositoryLocation = self._request.getRepositoryLocation()
        if repositoryLocation.isRecognizable():
            canonicalRepoNameOrUrl = repositoryLocation.getCanonicalName()
        else:
            canonicalRepoNameOrUrl = self._url

        return "{nameOrID} : {repoNameOrURL} --> {requestType}".format(
            nameOrID=nameOrID,
            repoNameOrURL=canonicalRepoNameOrUrl,
            requestType=self._request.__class__.__name__
        )

    def getProjectID(self) -> str:
        return self._projectID

    def getProjectName(self) -> str:
        return self._projectName

    def getURL(self) -> str:
        return self._url

    def getResponseDescription(self) -> str:
        assert isinstance(self._request, RepositoryRoutineRequestModel)
        repositoryLocation = self._request.getRepositoryLocation()
        if repositoryLocation.isRecognizable():
            canonicalRepoNameOrUrl = repositoryLocation.getCanonicalName()
        else:
            canonicalRepoNameOrUrl = self._url
        assert self._response is not None
        if self._response.wasSuccessful():
            return "✅ Routine ({repoNameOrURL} --> {requestType}) was successful!".format(
                repoNameOrURL=canonicalRepoNameOrUrl,
                requestType=self.getRequest().__class__.__name__
            )
        else:
            return "❌ Routine ({repoNameOrURL} --> {requestType}) failed. Reason: {reason}".format(
                repoNameOrURL=canonicalRepoNameOrUrl,
                requestType=self.getRequest().__class__.__name__,
                reason=self.getResponse().getMessage())


class ManagerExternalCommandLineToolTask(ManagerTask):
    """
    This Task class wraps requests and responses for ExternalCommandLineToolRoutines.
    """

    def __init__(self, request: BaseRequestModel) -> None:
        super().__init__(request)

    def getResponseDescription(self) -> str:
        """
        Generate a string that describes the response to the request in a human-readable
        way.
        """
        assert self._response is not None
        if self._response.wasSuccessful():
            return "✅ External Command Line Tool Request ({requestType}) was successful!".format(
                requestType=self.getRequest().__class__.__name__)
        else:
            return "❌ External Command Line Tool Request ({requestType}) failed. Reason: {reason}".format(
                requestType=self.getRequest().__class__.__name__, reason=self.getResponse().getMessage())


class ManagerAnalysisTask(ManagerTask):
    """
    This Task class wraps requests and responses for DataAnalyses.
    """

    def __init__(self, request: BaseRequestModel) -> None:
        super().__init__(request)

    def getResponseDescription(self) -> str:
        assert self._response is not None
        if self._response.wasSuccessful():
            return "✅ Analysis ({requestType}) was successful!".format(
                requestType=self.getRequest().__class__.__name__
            )
        else:
            return "❌ Analysis ({requestType}) failed. Reason: {reason}".format(
                requestType=self.getRequest().__class__.__name__,
                reason=self.getResponse().getMessage()
            )


class ReposcannerManager:
    """
    The ReposcannerRoutineManager is responsible for launching and tracking executions
    of RepositoryRoutines and DataAnalyses. The frontend creates an instance of this manager and
    passes the necessary repository and credential data to it.
    """

    def __init__(
            self,
            notebook: Optional[AbstractLabNotebook] = None,
            outputDirectory: str = "./",
            workspaceDirectory: str = "./",
            gui: bool = False,
    ) -> None:
        self._notebook = notebook
        self._repositoryRoutines: List[RepositoryRoutine] = []
        self._externalCommandLineToolRoutines: List[ExternalCommandLineToolRoutine] = []
        self._analyses: List[DataAnalysis] = []
        self._tasks: List[ManagerRepositoryRoutineTask] = []
        self._keychain: Optional[CredentialKeychain] = None
        self._outputDirectory = outputDirectory
        self._workspaceDirectory = workspaceDirectory
        self._guiModeEnabled = gui
        self._store = DataEntityStore()

    @staticmethod
    def dynamicallyImportFrom(name: str) -> Any:
        if ":" not in name:
            warnings.warn(
                "Unqualified routine names ({}) are deprecated. "
                "Use <module>.<RoutineClassName> or <package>.<module>:<RoutineClassName>."
                .format(name),
                DeprecationWarning,
            )
            import reposcanner.contrib, reposcanner.dummy
            if hasattr(reposcanner.contrib, name):
                return getattr(reposcanner.contrib, name)
            elif hasattr(reposcanner.dummy, name):
                return getattr(reposcanner.dummy, name)
            elif name in globals():
                return globals()[name]
            else:
                raise ValueError(
                    "{} not found in the default search locations."
                    .format(name)
                )
        else:
            importName, _, objectName = name.partition(":")
            module = importlib.import_module(importName)
            return getattr(module, objectName)


    def initializeRoutinesAndAnalyses(self, configData: Dict[str, Any]) -> None:
        """Constructs RepositoryRoutine and DataAnalysis objects that belong to the manager."""

        for routineEntry in configData.get('routines', []):
            if isinstance(routineEntry, dict):
                # The routineEntry is a dictionary, implying it
                # has parameters we need to pass to the
                # constructor. Otherwise it'll just be a plain string.
                routineName = list(routineEntry.keys())[0]
                configParameters = routineEntry[routineName]
            elif isinstance(routineEntry, str):
                routineName = routineEntry
                configParameters = None
            else:
                raise TypeError("Invalid routine: {} ({})"
                                .format(routineEntry, type(routineEntry)))

            routineClazz = self.dynamicallyImportFrom(routineName)
            routineInstance = routineClazz()
            routineInstance.setConfigurationParameters(configParameters)

            if isinstance(routineInstance, RepositoryRoutine):
                self._repositoryRoutines.append(routineInstance)
            elif isinstance(routineInstance, ExternalCommandLineToolRoutine):
                self._externalCommandLineToolRoutines.append(routineInstance)
            else:
                raise TypeError(
                    "ReposcannerManager does not know how to handle this "
                    "routine type: {}"
                    .format(type(routineInstance))
                )

        for analysisEntry in configData.get('analyses', []):
            if isinstance(analysisEntry, dict):
                # The analysisEntry is a dictionary, implying it
                # has parameters we need to pass to the
                # constructor. Otherwise it'll just be a plain string.
                analysisName = list(analysisEntry.keys())[0]
                configParameters = analysisEntry[analysisName]
            elif isinstance(analysisEntry, str):
                analysisName = analysisEntry
                configParameters = None
            else:
                raise TypeError("Invalid analysis: {} ({})"
                                .format(analysisName, type(analysisName)))
            analysisClazz = self.dynamicallyImportFrom(analysisName)
            analysisInstance = analysisClazz()
            analysisInstance.setConfigurationParameters(configParameters)

            if isinstance(analysisInstance, DataAnalysis):
                self._analyses.append(analysisInstance)
            else:
                raise TypeError(
                    "ReposcannerManager does not know how to handle this "
                    "analysis type: {}"
                    .format(type(analysisInstance))
                )

        for r_routine in self._repositoryRoutines:
            if self._notebook is not None:
                self._notebook.onRoutineCreation(r_routine)
        for cmd_routine in self._externalCommandLineToolRoutines:
            if self._notebook is not None:
                self._notebook.onRoutineCreation(cmd_routine)
        for analysis in self._analyses:
            if self._notebook is not None:
                self._notebook.onAnalysisCreation(analysis)

    def addDataEntityToStore(self, entity: ReposcannerDataEntity) -> None:
        """
        Allows the user to add additional data to the DataEntityStore
        prior to execution (e.g. from reposcanner-data)
        """
        self._store.insert(entity)

    def getRoutines(self) -> Sequence[DataMiningRoutine]:
        """
        Provides a list of all routines
        available for the manager to delgate tasks to.
        Used for testing purposes.
        """
        return (*self._repositoryRoutines, *self._externalCommandLineToolRoutines)

    def getRepositoryRoutines(self) -> Sequence[RepositoryRoutine]:
        """
        Provides a list of repository-mining routines
        available for the manager to delgate tasks to.
        Used for testing purposes.
        """
        return self._repositoryRoutines

    def getExternalCommandLineToolRoutines(self) -> Sequence[ExternalCommandLineToolRoutine]:
        """
        Provides a list of external command-line tool routines
        available for the manager to delgate tasks to.
        Used for testing purposes.
        """
        return self._externalCommandLineToolRoutines

    def getAnalyses(self) -> Sequence[DataAnalysis]:
        """
        Provides a list of analyses available for the manager
        to delgate tasks to. Used for testing purposes.
        """
        return self._analyses

    def isGUIModeEnabled(self) -> bool:
        return self._guiModeEnabled

    def buildTask(self, projectID: str, projectName: str, url: str, routineOrAnalysis: Union[DataMiningRoutine, DataAnalysis]) -> ManagerTask:
        """Constructs a task to hold a request/response pair."""
        requestType = routineOrAnalysis.getRequestType()
        if issubclass(requestType, ExternalCommandLineToolRoutineRequest):
            cmd_request = requestType(outputDirectory=self._outputDirectory)
            cmd_task = ManagerExternalCommandLineToolTask(cmd_request)
            return cmd_task
        elif issubclass(requestType, OnlineRoutineRequest):
            online_request = requestType(repositoryURL=url,
                                  outputDirectory=self._outputDirectory,
                                  keychain=self._keychain)
            online_task = ManagerRepositoryRoutineTask(
                projectID=projectID, projectName=projectName, url=url, request=online_request)
            return online_task
        elif issubclass(requestType, RepositoryRoutineRequestModel):
            repo_request = requestType(repositoryURL=url,
                                  outputDirectory=self._outputDirectory,
                                  workspaceDirectory=self._workspaceDirectory) # type: ignore
            repo_task = ManagerRepositoryRoutineTask(
                projectID=projectID, projectName=projectName, url=url, request=repo_request)
            return repo_task
        elif issubclass(requestType, AnalysisRequestModel):
            analysis_request = requestType()
            analysis_task = ManagerAnalysisTask(analysis_request)
            return analysis_task
        else:
            raise TypeError(
                "Encountered unrecognized request type when building task: {requestType}.".format(
                    requestType=requestType))

    def prepareTasks(
            self,
            repositoryDictionary: Dict[str, Dict[str, Any]],
            credentialsDictionary: Dict[str, Dict[str, str]],
    ) -> None:
        """Interpret the user's inputs so we know what repositories we need to
        collect data on and how we can access them."""
        self._keychain = CredentialKeychain(credentialsDictionary)
        for projectID in repositoryDictionary:
            projectEntry = repositoryDictionary[projectID]
            if "name" in projectEntry:
                projectName = projectEntry["name"]
            else:
                projectName = ""

            for url in projectEntry["urls"]:
                for routine in self._repositoryRoutines:
                    task = self.buildTask(projectID, projectName, url, routine)
                    if self._notebook is not None:
                        self._notebook.onTaskCreation(task)
                    if not isinstance(task, ManagerRepositoryRoutineTask):
                        raise TypeError("Tasks must be ManagerRepositoryRoutineTask not {}".format(type(task)))
                    self._tasks.append(task)
        for analysis in self._analyses:
            task = self.buildTask(projectID, projectName, url, analysis)
            if self._notebook is not None:
                self._notebook.onTaskCreation(task)
            if not isinstance(task, ManagerRepositoryRoutineTask):
                raise TypeError("Tasks must be ManagerRepositoryRoutineTask not {}".format(type(task)))
            self._tasks.append(task)

    def run(self, repositoriesDataFile: YAMLData, credentialsDataFile: YAMLData, configDataFile: YAMLData) -> None:
        """
        run() is the primary method that is called by the main function.
        This method starts Reposcanner's execution.
        """
        self.initializeRoutinesAndAnalyses(configDataFile.getData())
        self.prepareTasks(repositoriesDataFile.getData(), credentialsDataFile.getData())

        if not self.isGUIModeEnabled():
            self.executeWithNoGUI()
        else:
            self.executeWithGUI()

    def executeWithNoGUI(self) -> None:
        """
        Plain-text execution mode.
        """
        for task in tqdm(self._tasks):
            assert self._notebook is not None
            #s: Tuple[Union[DataMiningRoutine, DataAnalysis], ...] = 
            task.process(
                (*self._repositoryRoutines, *self._externalCommandLineToolRoutines, *self._analyses),
                self._store,
                self._notebook)
            response = task.getResponse()
            print(task.getResponseDescription())
            if not task.getResponse().wasSuccessful():
                for attachment in response.getAttachments():
                    print(attachment)
            for attachment in response.getAttachments():
                if isinstance(attachment, ReposcannerDataEntity):
                    self._store.insert(attachment)
                else:
                    print("Cannot store attachment of type {attachmentType}".format(attachmentType=str(type(attachment))))

    def executeWithGUI(self) -> None:
        """
        Fancy Curses-based GUI execution mode.
        """
        def centerTextPosition(text: str, windowWidth: int) -> int:
            half_length_of_text = int(len(text) / 2)
            middle_column = int(windowWidth / 2)
            x_position = middle_column - half_length_of_text
            return x_position

        try:
            screen = curses.initscr()
            screenHeight, screenWidth = screen.getmaxyx()

            header = curses.newwin(3, screenWidth, 0, 0)
            title = "🔎 Reposcanner: The IDEAS-ECP PSIP Team Repository Scanner 🔎"
            header.border(2)
            header.addstr(
                1,
                centerTextPosition(
                    title,
                    screenWidth),
                title,
                curses.A_BOLD)
            header.refresh()

            footer = curses.newwin(3, screenWidth, screenHeight - 3, 0)
            footer.border(2)
            footer.refresh()

            upcomingRequestsWindowHeight = screenHeight // 4
            upcomingRequestsWindowWidth = int(screenWidth * 0.8)
            upcomingRequestsWindow = curses.newwin(
                upcomingRequestsWindowHeight, upcomingRequestsWindowWidth, 5, int(
                    screenWidth * 0.1))
            upcomingRequestsWindow.border(2)
            upcomingRequestsWindow.refresh()

            messageWindowHeight = screenHeight // 4
            messageWindowWidth = int(screenWidth * 0.8)
            messageWindow = curses.newwin(upcomingRequestsWindowHeight,
                                          upcomingRequestsWindowWidth,
                                          5 + 4 + upcomingRequestsWindowHeight,
                                          int(screenWidth * 0.1))
            messageWindow.border(2)
            messageWindow.refresh()
            messages: List[str] = []
            messageLimit = messageWindowHeight - 4
            messages.insert(0, "Reposcanner Initalized")

            header = curses.newwin(3, screenWidth, 0, 0)

            for i in range(len(self._tasks)):
                currentTask = self._tasks[i]

                # Keep header visible
                header.border(2)
                header.addstr(
                    1,
                    centerTextPosition(
                        title,
                        screenWidth),
                    title,
                    curses.A_BOLD)
                header.refresh()

                # Show upcoming requests
                upcomingTasks = self._tasks[i:min(
                    i + upcomingRequestsWindowHeight - 4, len(self._tasks) - 1)]
                upcomingRequestsTitle = "Upcoming Requests"
                upcomingRequestsWindow.addstr(
                    1,
                    centerTextPosition(
                        upcomingRequestsTitle,
                        upcomingRequestsWindowWidth),
                    upcomingRequestsTitle,
                    curses.A_BOLD)
                for j in range(len(upcomingTasks)):
                    description = upcomingTasks[j].getDescription()
                    description = (description[:upcomingRequestsWindowWidth - 3] + '..') if len(
                        description) > upcomingRequestsWindowWidth - 3 else description
                    upcomingRequestsWindow.addstr(
                        j + 2, 1, upcomingTasks[j].getDescription())
                upcomingRequestsWindow.border(2)
                upcomingRequestsWindow.refresh()

                # Show response messages
                messageWindow.refresh()
                messageWindow.clear()
                messageWindowTitle = "Messages"
                messageWindow.addstr(
                    1,
                    centerTextPosition(
                        messageWindowTitle,
                        messageWindowWidth),
                    messageWindowTitle,
                    curses.A_BOLD)
                messages = messages[0:min(messageLimit, len(messages))]
                for j in range(len(messages)):
                    message = messages[j]
                    message = (message[0:messageWindowWidth - 3] +
                               '..') if len(message) > messageWindowWidth - 3 else message
                    messageWindow.addstr(j + 2, 2, message)
                messageWindow.border(2)
                messageWindow.refresh()

                total = len(self._tasks)
                description = currentTask.getDescription()
                taskDescription = "(⏳ {i}/{total}) Processing: {description}".format(
                    i=i + 1, total=total, description=description)

                footer.addstr(1, 4, taskDescription, curses.A_BOLD)
                footer.border(2)
                footer.refresh()
                assert self._notebook is not None
                currentTask.process(
                    (*self._repositoryRoutines, *self._analyses),
                    self._store,
                    self._notebook)
                for attachment in currentTask.getResponse().getAttachments():
                    if isinstance(attachment, ReposcannerDataEntity):
                        self._store.insert(attachment)
                    else:
                        print("Cannot store attachment of type {attachmentType}".format(attachmentType=str(type(attachment))))

                messages.insert(0, currentTask.getResponseDescription())
                screen.refresh()

            curses.napms(5000)
        except Exception as exception:
            raise exception
        finally:
            screen.clear()
            curses.endwin()
