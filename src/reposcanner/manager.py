from reposcanner.contrib import ContributorAccountListRoutine,OfflineCommitCountsRoutine
from reposcanner.commitAuthors import AuthorAccountListRoutine
from reposcanner.dummy import DummyOfflineRoutine,DummyOnlineRoutine,DummyAnalysis
from reposcanner.git import CredentialKeychain
from reposcanner.data import DataEntityStore
from reposcanner.response import ResponseFactory
import datetime, logging, curses, sys
from tqdm import tqdm #For progress checking in non-GUI mode.
from abc import ABC, abstractmethod


class TaskFactory:
        def createManagerRoutineTask(self,projectID,projectName,url,request):
                return ManagerRoutineTask(projectID,projectName,url,request)
        def createManagerAnalysisTask(self,request):
                return ManagerAnalysisTask(request)
        

        
class ManagerTask(ABC):
        """Abstract base class for Task objects. Task objects are simple wrappers around
        requests and responses that makes it easier for the frontend to display execution
        progress."""
        
        def __init__(self,request):
                self._request = request
                self._response = None
        
        def getRequestClassName(self):
                return self._request.__class__.__name__
                
        def getRequest(self):
                return self._request
                
        def hasResponse(self):
                return self._response is not None
                
        def getResponse(self):
                return self._response
                
        def process(self,agents,store,notebook):
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
                                notebook.onTaskStart(self,store,selectedAgent)
                        if self._request.isAnalysisRequestType():
                                self._request.fetchDataFromStore(store)
                        self._response = selectedAgent.run(self._request)
                        if notebook is not None:
                                notebook.onTaskCompletion(self,selectedAgent)
                else:
                        responseFactory = ResponseFactory()
                        self._response = responseFactory.createFailureResponse(
                                message= "No routine/analysis was found that could \
                                execute the request ({requestType}).".format(
                                requestType=type(request)))
        
        @abstractmethod
        def getResponseDescription(self):
                """
                Generate a string that describes the response to the request in a human-readable
                way.
                """
                pass
        

class ManagerRoutineTask(ManagerTask):
        """
        This Task class wraps requests and responses for RepositoryRoutines.
        """
        def __init__(self,projectID,projectName,url,request):
                super().__init__(request)
                self._projectID = projectID
                self._projectName = projectName
                self._url = url
                                
        def getDescription(self):
                """
                Generates a string that describes the task.
                """
                if self._projectName is not None and len(self._projectName) > 0:
                        nameOrID = self._projectName
                else:
                        nameOrID = self._projectID
                        
                repositoryLocation = self._request.getRepositoryLocation()
                if repositoryLocation.isRecognizable():
                        canonicalRepoNameOrUrl = repositoryLocation.getCanonicalName()
                else:
                        canonicalRepoNameOrUrl = self._url
                
                return "{nameOrID} : {repoNameOrURL} --> {requestType}".format(
                        nameOrID = nameOrID,
                        repoNameOrURL = canonicalRepoNameOrUrl,
                        requestType = self._request.__class__.__name__
                )
                
        def getProjectID(self):
                return self._projectID
                
        def getProjectName(self):
                return self._projectName
                
        def getURL(self):
                return self._url
                                
        def getResponseDescription(self):
                repositoryLocation = self.getRequest().getRepositoryLocation()
                if repositoryLocation.isRecognizable():
                        canonicalRepoNameOrUrl = repositoryLocation.getCanonicalName()
                else:
                        canonicalRepoNameOrUrl = self._url
                
                if self._response.wasSuccessful():
                        return "✅ Routine ({repoNameOrURL} --> {requestType}) was successful!".format(
                                repoNameOrURL = canonicalRepoNameOrUrl,
                                requestType = self.getRequest().__class__.__name__
                        )
                else:
                        return "❌ Routine ({repoNameOrURL} --> {requestType}) failed. Reason: {reason}".format(
                                repoNameOrURL = canonicalRepoNameOrUrl,
                                requestType = self.getRequest().__class__.__name__,
                                reason=self.getResponse().getMessage()
                        )
                        
class ManagerAnalysisTask(ManagerTask):
        """
        This Task class wraps requests and responses for DataAnalyses.
        """
        def __init__(self,request):
                super().__init__(request)
        
        def getResponseDescription(self):
                if self._response.wasSuccessful():
                        return "✅ Analysis ({requestType}) was successful!".format(
                                requestType = self.getRequest().__class__.__name__
                        )
                else:
                        return "❌ Analysis ({requestType}) failed. Reason: {reason}".format(
                                requestType = self.getRequest().__class__.__name__,
                                reason=self.getResponse().getMessage()
                        )
                        

class ReposcannerManager:
        """
        The ReposcannerRoutineManager is responsible for launching and tracking executions
        of RepositoryRoutines and DataAnalyses. The frontend creates an instance of this manager and
        passes the necessary repository and credential data to it.
        """
        def __init__(self,notebook=None,outputDirectory="./",workspaceDirectory="./",gui=False):
                self._notebook = notebook
                self._routines = []
                self._analyses = []
                self._tasks = []
                self._keychain = None
                self._outputDirectory = outputDirectory
                self._workspaceDirectory = workspaceDirectory
                self._guiModeEnabled = gui
                self._store = DataEntityStore()
                
        def initializeRoutinesAndAnalyses(self,configData):
                """Constructs RepositoryRoutine and DataAnalysis objects that belong to the manager."""
                
                if 'routines' in configData:
                        for routineName in configData['routines']:
                                try:
                                        routineClazz = getattr(sys.modules[__name__], routineName)
                                        routineInstance = routineClazz()
                                        self._routines.append(routineInstance)
                                except:
                                        raise ValueError("Can't find routine matching name {name}".format(name=routineName))
                                        
                if 'analyses' in configData:
                        for analysisName in configData['analyses']:
                                try:
                                        analysisClazz = getattr(sys.modules[__name__], analysisName)
                                        analysisInstance = analysisClazz()
                                        self._analyses.append(analysisInstance)
                                except:
                                        raise ValueError("Can't find analysis matching name {name}".format(name=analysisName))     
                
                for routine in self._routines:
                        if self._notebook is not None:
                                self._notebook.onRoutineCreation(routine)
                for analysis in self._analyses:
                        if self._notebook is not None:
                                self._notebook.onAnalysisCreation(analysis)
        
        
        def addDataEntityToStore(self,entity):
                """
                Allows the user to add additional data to the DataEntityStore
                prior to execution (e.g. from reposcanner-data)
                """
                self._store.insert(entity)
        
                               
        def getRoutines(self):
                """
                Provides a list of routines available for the manager
                to delgate tasks to. Used for testing purposes.
                """
                return self._routines
                
        def getAnalyses(self):
                """
                Provides a list of analyses available for the manager
                to delgate tasks to. Used for testing purposes.
                """
                return self._analyses
                
        def isGUIModeEnabled(self):
                return self._guiModeEnabled
                
        def buildTask(self,projectID,projectName,url,routineOrAnalysis):
                """Constructs a task to hold a request/response pair."""
                requestType = routineOrAnalysis.getRequestType()
                
                if requestType.isRoutineRequestType():
                        if requestType.requiresOnlineAPIAccess():
                                request = requestType(repositoryURL=url,
                                outputDirectory=self._outputDirectory,
                                keychain=self._keychain)
                        else:
                                request = requestType(repositoryURL=url,
                                outputDirectory=self._outputDirectory,
                                workspaceDirectory=self._workspaceDirectory)
                        task = ManagerRoutineTask(projectID=projectID,projectName=projectName,url=url,request=request)
                        return task
                elif requestType.isAnalysisRequestType():
                        request = requestType()
                        task = ManagerAnalysisTask(request)
                        return task
                else:
                        raise TypeError("Encountered unrecognized request type when building task: {requestType}.".format(
                        requestType=requestType))
        
        def prepareTasks(self,repositoryDictionary,credentialsDictionary):
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
                                   for routine in self._routines:
                                           task = self.buildTask(projectID,projectName,url,routine)
                                           if self._notebook is not None:
                                                   self._notebook.onTaskCreation(task)
                                           self._tasks.append(task)
                for analysis in self._analyses:
                        task = self.buildTask(projectID,projectName,url,analysis)
                        if self._notebook is not None:
                                self._notebook.onTaskCreation(task)
                        self._tasks.append(task)
                
        def run(self,repositoriesDataFile,credentialsDataFile,configDataFile):
                """
                run() is the primary method that is called by the main function.
                This method starts Reposcanner's execution.
                """
                self.initializeRoutinesAndAnalyses(configDataFile.getData())
                self.prepareTasks(repositoriesDataFile.getData(),credentialsDataFile.getData())
                
                if not self.isGUIModeEnabled():
                        self.executeWithNoGUI()
                else:
                        self.executeWithGUI()
           
        def executeWithNoGUI(self):
                """
                Plain-text execution mode.
                """
                for task in tqdm(self._tasks):
                        task.process(self._routines+self._analyses,self._store,self._notebook)
                        response = task.getResponse()
                        print(task.getResponseDescription())
                        if not task.getResponse().wasSuccessful():
                            for attachment in response.getAttachments():
                                print(attachment)
                        for attachment in response.getAttachments():
                                self._store.insert(attachment)
                                
        def executeWithGUI(self):
                """
                Fancy Curses-based GUI execution mode.
                """
                def centerTextPosition(text,windowWidth):
                        half_length_of_text = int(len(text) / 2)
                        middle_column = int(windowWidth / 2)
                        x_position = middle_column - half_length_of_text
                        return x_position
                        
                try:
                        screen = curses.initscr()
                        screenHeight,screenWidth = screen.getmaxyx()
                
                        header = curses.newwin(3, screenWidth, 0, 0)
                        title = "🔎 Reposcanner: The IDEAS-ECP PSIP Team Repository Scanner 🔎"
                        header.border(2)
                        header.addstr(1,centerTextPosition(title,screenWidth),title,curses.A_BOLD)
                        header.refresh()
                
                        footer = curses.newwin(3, screenWidth, screenHeight-3, 0)
                        footer.border(2)
                        footer.refresh()
                
                        upcomingRequestsWindowHeight = screenHeight//4
                        upcomingRequestsWindowWidth = int(screenWidth * 0.8)
                        upcomingRequestsWindow = curses.newwin(upcomingRequestsWindowHeight, upcomingRequestsWindowWidth, 5, int(screenWidth*0.1))
                        upcomingRequestsWindow.border(2)
                        upcomingRequestsWindow.refresh()
                        
                        messageWindowHeight = screenHeight//4
                        messageWindowWidth = int(screenWidth * 0.8)
                        messageWindow = curses.newwin(upcomingRequestsWindowHeight, upcomingRequestsWindowWidth, 5+4+upcomingRequestsWindowHeight, int(screenWidth*0.1))
                        messageWindow.border(2)
                        messageWindow.refresh()
                        messages = []
                        messageLimit = messageWindowHeight-4
                        messages.insert(0,"Reposcanner Initalized")
                
                
                        header = curses.newwin(3, screenWidth, 0, 0)
                
                        for i in range(len(self._tasks)):
                                currentTask = self._tasks[i]
                                
                                
                                #Keep header visible
                                header.border(2)
                                header.addstr(1,centerTextPosition(title,screenWidth),title,curses.A_BOLD)
                                header.refresh()
                                
                                #Show upcoming requests
                                upcomingTasks = self._tasks[i:min(i+upcomingRequestsWindowHeight-4,len(self._tasks)-1)]
                                upcomingRequestsTitle = "Upcoming Requests"
                                upcomingRequestsWindow.addstr(1,centerTextPosition(upcomingRequestsTitle,upcomingRequestsWindowWidth),upcomingRequestsTitle,curses.A_BOLD)
                                for j in range(len(upcomingTasks)):
                                        description = upcomingTasks[j].getDescription()
                                        description = (description[:upcomingRequestsWindowWidth-3] + '..') if len(description) > upcomingRequestsWindowWidth-3 else description
                                        upcomingRequestsWindow.addstr(j+2,1,upcomingTasks[j].getDescription())
                                upcomingRequestsWindow.border(2)
                                upcomingRequestsWindow.refresh()
                                
                                #Show response messages
                                messageWindow.refresh()
                                messageWindow.clear()
                                messageWindowTitle = "Messages"
                                messageWindow.addstr(1,centerTextPosition(messageWindowTitle,messageWindowWidth),messageWindowTitle,curses.A_BOLD)
                                messages = messages[0:min(messageLimit,len(messages))]
                                for j in range(len(messages)):
                                        message = messages[j]
                                        message = (message[0:messageWindowWidth-3] + '..') if len(message) > messageWindowWidth-3 else message
                                        messageWindow.addstr(j+2,2,message)
                                messageWindow.border(2)
                                messageWindow.refresh()
                                
                                total = len(self._tasks)
                                description=currentTask.getDescription()
                                taskDescription = "(⏳ {i}/{total}) Processing: {description}".format(i=i+1,
                                total=total,
                                description=description)
                        
                                footer.addstr(1,4,taskDescription,curses.A_BOLD)
                                footer.border(2)
                                footer.refresh()
                                currentTask.process(self._routines+self._analyses,self._store,self._notebook)
                                for attachment in currentTask.getResponse().getAttachments():
                                        self._store.insert(attachment)
                                
                                messages.insert(0,currentTask.getResponseDescription())
                                screen.refresh()
                                
                        curses.napms(5000)
                except Exception as exception:
                        raise exception
                finally:
                        screen.clear()
                        curses.endwin()
                        
                
                        
                        
                
                
        
