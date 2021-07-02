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

#def createReq(routine_name):
# return type(routine_name, (OnlineRoutineRequest,), {
#    '__init__': OnlineRoutineRequest.__init__} )

class AuthorAccountListRoutineRequest(OnlineRoutineRequest):
        def __init__(self,repositoryURL,outputDirectory,username=None,password=None,token=None,keychain=None):
                super().__init__(repositoryURL,outputDirectory,username=username,password=password,token=token,keychain=keychain)

class AuthorAccountListRoutine(OnlineRepositoryRoutine):
        """
        Contact the version control platform API, and get the account information of everyone who has ever contributed to the repository.
        """
        #TODO: StarGazersRoutine lacks a bitbucketImplementation(self,request,session) method.

        def getRequestType(self):
                return AuthorAccountListRoutineRequest

        def _replaceNoneWithEmptyString(self,value):
                if value is None:
                        return ""
                else:
                        return value

        def githubImplementation(self,request,session):
                factory = DataEntityFactory()
                # self.getRequestType().name
                output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_AuthorAccountListRoutine.csv".format(
                        outputDirectory=request.getOutputDirectory(),
                        repoName=request.getRepositoryLocation().getRepositoryName()))

                output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
                output.setCreator(self.__class__.__name__)
                output.setDateCreated(datetime.date.today())
                output.setURL(request.getRepositoryLocation().getURL())
                output.setColumnNames(["Author Name","Author Email(s)","Committer Name"," Committer Email(s)", "Created at"])
                output.setColumnDatatypes(["str","str","str","str", "int"])


                for pr in session.get_pulls(): # For API call efficiency specify the state of pull requests.
                    for c in pr.get_commits():
                        output.addRecord([
                            self._replaceNoneWithEmptyString(c.commit.author.name),
                            self._replaceNoneWithEmptyString(c.commit.author.email),
                            self._replaceNoneWithEmptyString(c.commit.committer.name),
                            self._replaceNoneWithEmptyString(c.commit.committer.email),
                            self._replaceNoneWithEmptyString(str(get_time(c.commit.author.date)))
                            ])

                output.writeToFile()
                responseFactory = ResponseFactory()
                return responseFactory.createSuccessResponse(
                        message="Completed!",attachments=output)

        def gitlabImplementation(self,request,session):
                contributors = [contributor for contributor in session.users.list()]
                output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_contributorAccounts.csv".format(
                        outputDirectory=request.getOutputDirectory(),
                        repoName=request.getRepositoryLocation().getRepositoryName()))

                output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
                output.setCreator(self.__class__.__name__)
                output.setDateCreated(datetime.date.today())
                output.setURL(request.getRepositoryLocation().getURL())
                output.setColumnNames(["Login Name","Actual Name","Email(s)"])
                output.setColumnDatatypes(["str","str","str"])

                contributors = [contributor for contributor in session.get_contributors()]
                for contributor in contributors:
                        output.addRecord([
                                self._replaceNoneWithEmptyString(contributor.username),
                                self._replaceNoneWithEmptyString(contributor.name),
                                ';'.join(contributor.emails.list())
                        ])
                output.writeToFile()
                responseFactory = ResponseFactory()
                return responseFactory.createSuccessResponse(
                        message="Completed!",attachments=output)
