from os import name
from reposcanner.routines import OfflineRepositoryRoutine,OnlineRepositoryRoutine
from reposcanner.analyses import DataAnalysis
from reposcanner.requests import OfflineRoutineRequest,OnlineRoutineRequest,AnalysisRequestModel
from reposcanner.response import ResponseFactory
from reposcanner.provenance import ReposcannerRunInformant
from reposcanner.data import DataEntityFactory
import pygit2

import time, datetime
import csv
import numpy as np

def get_time(dt):
    # >>> get_time(None):
    # None
    if dt is None:
        return None
    return int( dt.timestamp() )

def toStr(x):
    if x is None:
        return ""
    return x

#routines = {}
def declareRoutine(routine, github=None, gitlab=None, offline=None):
    """
    Declare a scanning routine with the given name and
    implementation set.

    TODO: maintain routines in reposcanner global
          (rather than import from manager.py)
    """
    #global routines

    def routineInit(self,*args,**kws):
        OnlineRoutineRequest.__init__(self,*args,**kws)

    RoutineRequest = type(f"{routine}RoutineRequest", (OnlineRoutineRequest,), {
                            '__init__': routineInit })
                          # 'name': routine } )
    
    operations = dict(
              getRequestType = lambda self: RoutineRequest,
              githubImplementation = github,
              gitlabImplementation = gitlab,
              offlineImplementation = offline
            )

    Routine = type(f"{routine}Routine", (OnlineRepositoryRoutine,), operations)
    #routines[routine] = Routine
    return Routine

def respondCSV(scanFunction):
    """
    Decorator to open a CSV file and wrap the results into a ResponseFactory.
    It metamorphoses a scanFunction into a classFunction.
    The classFunction has a bunch of boiler-plate code
    for logging, etc.  The scanFunction doesn't have to deal
    with all of that.  Instead, it queries its session object
    and puts data directly into the output csv-writer.
    """
    def classFunction(self, request, session):
        # Setup an output CSV file to hold the scan results
        #routine = self.getRequestType().name # my scan routine name

        routine = self.__class__.__name__ # my scan routine name
        output = DataEntityFactory().createAnnotatedCSVData(
            "{outputDirectory}/{repoOwner}_{repoName}_{routine}.csv".format(
                        outputDirectory = request.getOutputDirectory(),
                        repoOwner = request.getRepositoryLocation().getOwner(),
                        repoName = request.getRepositoryLocation().getRepositoryName(),
                        routine=routine))

        output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(routine)
        output.setDateCreated(datetime.date.today())
        output.setURL(request.getRepositoryLocation().getURL())

        ok, ret = scanFunction(output, session)
        responseFactory = ResponseFactory()
        if ok:
            output.writeToFile()
            return responseFactory.createSuccessResponse(
                            message="Completed!", attachments=ret)
        return responseFactory.createFailureResponse(
                        message="Error!", attachments=ret)

    return classFunction

@respondCSV
def githubImplementation(output, session):
    output.setColumnNames(["Author Name","Author Email(s)","Committer Name"," Committer Email(s)","Created at"])
    output.setColumnDatatypes(["str"]*4 + ["int"])

    for pr in session.get_pulls(): # For API call efficiency specify the state of pull requests.
        for c in pr.get_commits():
            output.addRecord([
                toStr(c.commit.author.name),
                toStr(c.commit.author.email),
                toStr(c.commit.committer.name),
                toStr(c.commit.committer.email),
                toStr(str(get_time(c.commit.author.date)))
                ])
    return True, output

@respondCSV
def gitlabImplementation(output, session):
    #contributors = [contributor for contributor in session.users.list()]
    output.setColumnNames(["Login Name","Actual Name","Email(s)"])
    output.setColumnDatatypes(["str","str","str"])

    contributors = [contributor for contributor in session.get_contributors()]
    for contributor in contributors:
                        output.addRecord([
                                toStr(contributor.username),
                                toStr(contributor.name),
                                ';'.join(contributor.emails.list())
                        ])
    return True, output

AuthorAccountListRoutine = declareRoutine( "AuthorAccountList",
                                           githubImplementation,
                                           gitlabImplementation )
