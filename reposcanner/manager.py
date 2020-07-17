from reposcanner.contrib import ContributionPeriodRoutine
from reposcanner.git import CredentialKeychain
import datetime


class ManagerTask:
        def __init__(projectID,projectName,url):
                pass

class ReposcannerRoutineManager:
        """
        The ReposcannerRoutineManager is responsible for launching and tracking executions
        of RepositoryAnalysisRoutines. The frontend creates an instance of this manager and
        passes the necessary repository and credential data to it.
        """
        def __init__(self):
                self._routines = []
                self._initializeRoutines()
                self._startTime = None
                self._requests = {}
                self._keychain = None
                
        def _initializeRoutines(self):
                """Constructs RepositoryAnalysisRoutine objects that belong to the manager."""
                contributionPeriodRoutine = ContributionPeriodRoutine()
                self._routines.append(contributionPeriodRoutine)
        
        def _prepareRequests(self,repositoryDictionary,credentialsDictionary):
                """Interpret the user's inputs so we know what repositories we need to
                collect data on and how we can access them."""
                self._keychain = CredentialKeychain(credentialsDictionary)
                for projectId in repositoryDictionary:
                           projectEntry = repositoryDictionary[projectId]
                           if "name" in projectEntry:
                                   projectName = projectEntry["name"]
                           for url in projectEntry["urls"]:
                                   pass    
                
        def run(self,repositoryDictionary,credentialsDictionary):
                self._startTime = datetime.datetime.today()
                self._loadUserData(repositoryDictionary,credentialsDictionary)
                
                
        