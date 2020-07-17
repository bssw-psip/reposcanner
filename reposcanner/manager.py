from reposcanner.contrib import ContributionPeriodRoutine

class ReposcannerRoutineManager:
        """
        The ReposcannerRoutineManager is responsible for launching and tracking executions
        of RepositoryAnalysisRoutines. The frontend creates an instance of this manager and
        passes the necessary repository and credential data to it.
        """
        def __init__(self):
                self._routines = []
                self._initializeRoutines()
                
        def _initializeRoutines(self):
                """Constructs RepositoryAnalysisRoutine objects that belong to the manager."""
                contributionPeriodRoutine = ContributionPeriodRoutine()
                self._routines.append(contributionPeriodRoutine)
                
        def run(self,repositoryDictionary,credentialsDictionary):
                pass
                
                
        