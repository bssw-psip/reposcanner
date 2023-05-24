from reposcanner.routines import OfflineRepositoryRoutine, OnlineRepositoryRoutine
from reposcanner.analyses import DataAnalysis
from reposcanner.requests import OfflineRoutineRequest, OnlineRoutineRequest, AnalysisRequestModel
from reposcanner.response import ResponseFactory
from reposcanner.provenance import ReposcannerRunInformant
from reposcanner.data import DataEntityFactory
import pygit2

from pathlib import Path
import time
import datetime
import re
import csv
import pandas as pd
import numpy as np
import inspect


def get_time(dt):
    if dt is None:
        return None
    return int( dt.timestamp() )

def _replaceNoneWithEmptyString(value):
    if value is None:
        return ""
    else:
        return value



# Routine to scrape general info about GitHub project (in the form of a
# kanban board), specifically:
#  Unique project ID, date/time of creation, creator login, 
#  name, body text, names of columms, state, date/time last updated

class KanbanProjectOverviewRoutineRequest(OnlineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, \
        username=None, password=None, token=None, keychain=None):
        super().__init__(repositoryURL, outputDirectory, \
            username=username, password=password, token=token, keychain=keychain)

class KanbanProjectOverviewRoutine(OnlineRepositoryRoutine):

    def getRequestType(self):
        return KanbanProjectOverviewRoutineRequest

    def githubImplementation(self, request, session):
        factory = DataEntityFactory()
        output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_KanbanProjectOverview.csv".format(\
            outputDirectory=request.getOutputDirectory(), \
            repoName=request.getRepositoryLocation().getRepositoryName()))

        output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(self.__class__.__name__)
        output.setDateCreated(datetime.date.today())
        output.setURL(request.getRepositoryLocation().getURL())
        output.setColumnNames(["projectID", \
            "dateCreated", \
            "creatorLogin", \
            "projectName", \
            "bodyText", \
            "columnNames", \
            "projectState", \
            "dateLastUpdated"])
        output.setColumnDatatypes(["int", \
            "int", \
            "str", \
            "str", \
            "str", \
            "str", \
            "str", \
            "int"])

        projects = session.get_projects(state="all")
        for project in projects:
            projectID = project.id
            datetimeCreated = get_time(project.created_at)
            creatorLogin = _replaceNoneWithEmptyString(\
                project.creator.login)
            projectName = _replaceNoneWithEmptyString(\
                project.name)
            bodyText = _replaceNoneWithEmptyString(\
                project.body)
            columnNames = [_replaceNoneWithEmptyString(column.name) \
                for column in project.get_columns()]
            projectState = _replaceNoneWithEmptyString(\
                project.state)
            if project.updated_at is not None:
                datetimeUpdated = get_time(project.updated_at)
            else:
                datetimeUpdated = datetimeCreated

            output.addRecord([projectID, \
                datetimeCreated, \
                creatorLogin, \
                projectName, \
                bodyText, \
                ";".join(columnNames), \
                projectState, \
                datetimeUpdated])

        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(\
            message="KanbanProjectOverviewRoutine completed!", attachments=output)

    def gitlabImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass

    def bitbucketImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass



# Routine to scrape data from cards in each column of projects
#  Specifically, includes:
#   Unique project ID (for overall Kanban project), date/time of creation,
#   creator login, column name, associated issue/pull request ID,
#   datetime of last update

class KanbanProjectDetailsRoutineRequest(OnlineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, \
        username=None, password=None, token=None, keychain=None):
        super().__init__(repositoryURL, outputDirectory, \
            username=username, password=password, token=token, keychain=keychain)

class KanbanProjectDetailsRoutine(OnlineRepositoryRoutine):

    def getRequestType(self):
        return KanbanProjectDetailsRoutineRequest

    def githubImplementation(self, request, session):
        factory = DataEntityFactory()
        output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_KanbanProjectDetails.csv".format(\
            outputDirectory=request.getOutputDirectory(), \
            repoName=request.getRepositoryLocation().getRepositoryName()))

        output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(self.__class__.__name__)
        output.setDateCreated(datetime.date.today())
        output.setURL(request.getRepositoryLocation().getURL())
        output.setColumnNames(["projectID", \
            "dateCreated", \
            "creatorLogin", \
            "columnName", \
            "associatedIssueOrPullRequestID", \
            "dateLastUpdated"])
        output.setColumnDatatypes(["int", \
            "int", \
            "str", \
            "str", \
            "str", \
            "int"])

        projects = session.get_projects(state="all")
        for project in projects:
            projectID = project.id

            columns = project.get_columns()
            for column in columns:
                columnName = _replaceNoneWithEmptyString(\
                    column.name)
                
                cards = column.get_cards(archived_state="all")
                for card in cards:
                    datetimeCreated = get_time(card.created_at)
                    creatorLogin = _replaceNoneWithEmptyString(\
                        card.creator.login)
                    if card.get_content() is not None:
                        associatedID = _replaceNoneWithEmptyString(\
                            str(card.get_content().id))
                    else:
                        associatedID = ""
                    if card.updated_at is not None:
                        datetimeUpdated = get_time(card.updated_at)
                    else:
                        datetimeUpdated = datetimeCreated

                    output.addRecord([projectID, \
                        datetimeCreated, \
                        creatorLogin, \
                        columnName, \
                        associatedID, \
                        datetimeUpdated])

        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(\
            message="KanbanProjectDetailsRoutine completed!", attachments=output)

    def gitlabImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass

    def bitbucketImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass
