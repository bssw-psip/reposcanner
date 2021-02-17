from reposcanner.contrib import ContributorAccountListRoutine
from reposcanner.git import CredentialKeychain
from reposcanner.response import ResponseFactory
import datetime, logging, curses
from tqdm import tqdm #For progress checking in non-GUI mode.


class ManagerTask:
        """
        This is a simple wrapper around requests and responses that makes it
        easier for the frontend to display execution progress.
        """
        def __init__(self,projectID,projectName,url,request):
                self._projectID = projectID
                self._projectName = projectName
                self._url = url
                self._request = request
                self._response = None
        
        def process(self,routines,notebook):
                """
                Scan through a set of available routines and see if any can execute
                the request held by this task. If no routines can handle this request,
                this method will create a failure response and store it.
                
                routines: An iterable of RepositoryRoutine objects.
                """
                selectedRoutine = None
                for routine in routines:
                        if routine.canHandleRequest(self._request):
                                selectedRoutine = routine
                                break
                if selectedRoutine is not None:
                        if notebook is not None:
                                notebook.onTaskStart(self,selectedRoutine)     
                        self._response = selectedRoutine.run(self._request)
                        if notebook is not None:
                                notebook.onTaskCompletion(self,selectedRoutine)
                else:
                        responseFactory = ResponseFactory()
                        self._response = responseFactory.createFailureResponse(
                                message= "No routine was found that could \
                                execute the request ({requestType}).".format(
                                requestType=type(request)))
                                
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
                
        def getRequestClassName(self):
                return self._request.__class__.__name__
                
        def getURL(self):
                return self._url
                
        def getRequest(self):
                return self._response
                
        def getResponse(self):
                return self._response
                                
        def getResponseDescription(self):
                repositoryLocation = self._request.getRepositoryLocation()
                if repositoryLocation.isRecognizable():
                        canonicalRepoNameOrUrl = repositoryLocation.getCanonicalName()
                else:
                        canonicalRepoNameOrUrl = self._url
                
                if self._response.wasSuccessful():
                        return "✅ ({repoNameOrURL} --> {requestType}) was successful!".format(
                                repoNameOrURL = canonicalRepoNameOrUrl,
                                requestType = self._request.__class__.__name__
                        )
                else:
                        return "❌ ({repoNameOrURL} --> {requestType}) failed. Reason: {reason}".format(
                                repoNameOrURL = canonicalRepoNameOrUrl,
                                requestType = self._request.__class__.__name__,
                                reason=self._response.getMessage()
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
                self._initializeRoutines()
                self._tasks = []
                self._keychain = None
                self._outputDirectory = outputDirectory
                self._workspaceDirectory = workspaceDirectory
                self._guiModeEnabled = gui
                
        def _initializeRoutines(self):
                """Constructs RepositoryRoutine objects that belong to the manager."""
                #TODO: Replace this with a routine that initializes routines based on an
                #input config file.
                contributorAccountListRoutine = ContributorAccountListRoutine()
                self._routines.append(contributorAccountListRoutine)
                
                for routine in self._routines:
                        if self._notebook is not None:
                                self._notebook.onRoutineCreation(routine)
                
        def _buildTask(self,projectID,projectName,url,routine):
                """Constructs a task to hold a request/response pair."""
                requestType = routine.getRequestType()
                if requestType.requiresOnlineAPIAccess():
                        request = requestType(repositoryURL=url,
                                outputDirectory=self._outputDirectory,
                                keychain=self._keychain)
                else:
                        request = requestType(repositoryURL=url,
                                outputDirectory=self._outputDirectory,
                                workspaceDirectory=self._workspaceDirectory)
                
                task = ManagerTask(projectID=projectID,projectName=projectName,url=url,request=request)
                return task
        
        def _prepareTasks(self,repositoryDictionary,credentialsDictionary):
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
                                           task = self._buildTask(projectID,projectName,url,routine)
                                           if self._notebook is not None:
                                                   self._notebook.onTaskCreation(task)
                                           self._tasks.append(task)
                                           
                
        def run(self,repositoryDictionary,credentialsDictionary):
                #self._startTime = datetime.datetime.today()
                self._prepareTasks(repositoryDictionary,credentialsDictionary)
                
                if not self._guiModeEnabled:
                        self.executeWithNoGUI()
                else:
                        self.executeWithGUI()
                        
                        
        def executeWithNoGUI(self):
                for task in tqdm(self._tasks):
                        task.process(self._routines,self._notebook)
                        response = task.getResponseDescription()
                        print(response)
                                
        def executeWithGUI(self):
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
                                currentTask.process(self._routines,self._notebook)
                                
                                messages.insert(0,currentTask.getResponseDescription())
                                screen.refresh()
                                
                        curses.napms(5000)
                except Exception as exception:
                        raise exception
                finally:
                        screen.clear()
                        curses.endwin()
                        
                
                        
                        
                
                
        
