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
        
        def process(self,routines):
                """
                Scan through a set of available routines and see if any can execute
                the request held by this task. If no routines can handle this request,
                this method will create a failure response and store it.
                
                routines: An iterable of RepositoryAnalysisRoutine objects.
                """
                selectedRoutine = None
                for routine in routines:
                        if routine.canHandleRequest(self._request):
                                selectedRoutine = routine
                                break
                if selectedRoutine is not None:      
                        self._response = selectedRoutine.run(self._request)
                else:
                        responseFactory = ResponseFactory()
                        self._response = responseFactory.createFailureResponse(
                                message= "No routine was found that could \
                                execute the request ({requestType}).".format(
                                requestType=type(request)))
                                
        def getResponse(self):
                return self._response
                        
        def hasReceivedResponse(self):
                return self._response is not None

class ReposcannerRoutineManager:
        """
        The ReposcannerRoutineManager is responsible for launching and tracking executions
        of RepositoryAnalysisRoutines. The frontend creates an instance of this manager and
        passes the necessary repository and credential data to it.
        """
        def __init__(self,outputDirectory="./",workspaceDirectory="./",gui=False):
                self._routines = []
                self._initializeRoutines()
                self._startTime = None
                self._tasks = []
                self._keychain = None
                self._outputDirectory = outputDirectory
                self._workspaceDirectory = workspaceDirectory
                self._guiModeEnabled = gui
                
        def _initializeRoutines(self):
                """Constructs RepositoryAnalysisRoutine objects that belong to the manager."""
                contributorAccountListRoutine = ContributorAccountListRoutine()
                self._routines.append(contributorAccountListRoutine)
                
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
                                           self._tasks.append(task)
                                           
                
        def run(self,repositoryDictionary,credentialsDictionary):
                self._startTime = datetime.datetime.today()
                self._prepareTasks(repositoryDictionary,credentialsDictionary)
                
                if not self._guiModeEnabled:
                        self.executeWithNoGUI()
                else:
                        self.executeWithGUI()
                        
        def executeWithNoGUI(self):
                for task in tqdm(self._tasks):
                        task.process(self._routines)
                        response = task.getResponse()
                        if response.wasSuccessful():
                                print("Response: Success")
                                print("Message: {message}".format(message=response.getMessage()))
                        else:
                                print("Response: Failure")
                                print("Message: {message}".format(message=response.getMessage()))
                                
        def executeWithGUI(self):
                
                def centerTextPosition(text,windowWidth):
                        half_length_of_text = int(len(text) / 2)
                        middle_column = int(windowWidth / 2)
                        x_position = middle_column - half_length_of_text
                        return x_position
                
                screen = curses.initscr()
                screenHeight,screenWidth = screen.getmaxyx()
                
                header = curses.newwin(3, screenWidth, 0, 0)
                title = "🔎 Reposcanner: The IDEAS-ECP PSIP Team Repository Scanner 🔎"
                header.border(2)
                header.addstr(1,centerTextPosition(title,screenWidth),title,curses.A_BOLD)
                header.refresh()
                
                #for currentTask in self._tasks:
                #        break
                #        currentTask.process(self._routines)
                #        screen.refresh()
                
                curses.napms(5000)
                #screen.clear()
                curses.endwin()
                
                        
                        
                
                
        