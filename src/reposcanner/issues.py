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


def get_time(dt):
    if dt is None:
        return None
    return int( dt.timestamp() )

def _replaceNoneWithEmptyString(value):
    if value is None:
        return ""
    else:
        return value



# Routine to scrape general info about GitHub issues, specifically:
#  Unique issue ID, date/time of creation, creator login, assignee login(s),
#  title, label(s), state, date/time of closure, login of user who closed

class IssueOverviewRoutineRequest(OnlineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, \
        username=None, password=None, token=None, keychain=None):
        super().__init__(repositoryURL, outputDirectory, \
            username=username, password=password, token=token, keychain=keychain)

class IssueOverviewRoutine(OnlineRepositoryRoutine):

    def getRequestType(self):
        return IssueOverviewRoutineRequest

    def githubImplementation(self, request, session):
        factory = DataEntityFactory()
        output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_IssueOverview.csv".format(\
            outputDirectory=request.getOutputDirectory(), \
            repoName=request.getRepositoryLocation().getRepositoryName()))

        output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(self.__class__.__name__)
        output.setDateCreated(datetime.date.today())
        output.setURL(request.getRepositoryLocation().getURL())
        output.setColumnNames(["issueID", \
            "dateCreated", \
            "creatorLogin", \
            "assigneeLogins", \
            "issueTitle", \
            "labels", \
            "issueState", \
            "dateClosed", \
            "closerLogin"])
        output.setColumnDatatypes(["int", \
            "int", \
            "str", \
            "str", \
            "str", \
            "str", \
            "str", \
            "str", \
            "str"])

        issues = session.get_issues(state="all")
        for issue in issues:
            issueID = issue.id
            datetimeCreated = get_time(issue.created_at)
            creatorLogin = _replaceNoneWithEmptyString(\
                issue.user.login)
            assigneeList = [_replaceNoneWithEmptyString(user.login) \
                for user in issue.assignees]
            title = _replaceNoneWithEmptyString(\
                issue.title)
            labelList = [_replaceNoneWithEmptyString(label.name) \
                for label in issue.labels]
            issueState = _replaceNoneWithEmptyString(\
                issue.state)
            if issue.closed_at is not None:
                datetimeClosed = _replaceNoneWithEmptyString(\
                    str(get_time(issue.closed_at)))
            else:
                datetimeClosed = ""
            if issue.closed_by is not None:
                closerLogin = _replaceNoneWithEmptyString(\
                    issue.closed_by.login)
            else:
                closerLogin = ""

            output.addRecord([issueID, \
                datetimeCreated, \
                creatorLogin, \
                ";".join(assigneeList), \
                title, \
                ";".join(labelList), \
                issueState, \
                datetimeClosed, \
                closerLogin])

        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(\
            message="IssueOverviewRoutine completed!", attachments=output)

    def gitlabImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass

    def bitbucketImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass



# Routine to scrape natural language data from issues
#  Treats each "post" (i.e. original post and comments) as a separate entry
#  For each post, gets:
#   Unique issue ID (based on original post), type of post (original/comment),
#   date/time of creation, creator login, body text

class IssueDetailsRoutineRequest(OnlineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, \
        username=None, password=None, token=None, keychain=None):
        super().__init__(repositoryURL, outputDirectory, \
            username=username, password=password, token=token, keychain=keychain)

class IssueDetailsRoutine(OnlineRepositoryRoutine):

    def getRequestType(self):
        return IssueDetailsRoutineRequest

    def githubImplementation(self, request, session):
        factory = DataEntityFactory()
        output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_IssueDetails.csv".format(\
            outputDirectory=request.getOutputDirectory(), \
            repoName=request.getRepositoryLocation().getRepositoryName()))

        output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(self.__class__.__name__)
        output.setDateCreated(datetime.date.today())
        output.setURL(request.getRepositoryLocation().getURL())
        output.setColumnNames(["issueID", \
            "postType", \
            "dateCreated", \
            "creatorLogin", \
            "bodyText"])
        output.setColumnDatatypes(["int", \
            "str", \
            "int", \
            "str", \
            "str"])

        issues = session.get_issues(state="all")
        for issue in issues:
            issueID = issue.id
            datetimeCreated = get_time(issue.created_at)
            creatorLogin = _replaceNoneWithEmptyString(\
                issue.user.login)
            bodyText = _replaceNoneWithEmptyString(\
                issue.body)
            commentList = issue.get_comments()

            output.addRecord([issueID, \
                "original issue", \
                datetimeCreated, \
                creatorLogin, \
                bodyText])
            
            for comment in commentList:
                datetimeCreated = _replaceNoneWithEmptyString(\
                    str(get_time(comment.created_at)))
                creatorLogin = _replaceNoneWithEmptyString(\
                    comment.user.login)
                bodyText = _replaceNoneWithEmptyString(\
                    comment.body)
                output.addRecord([issueID, \
                    "issue comment", \
                    datetimeCreated, \
                    creatorLogin, \
                    bodyText])

        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(\
            message="IssueDetailsRoutine completed!", attachments=output)

    def gitlabImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass

    def bitbucketImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass
