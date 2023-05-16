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



# Routine to scrape general info about GitHub pull requests, specifically:
#  Unique issue ID, date/time of creation, creator login, assignee login(s),
#  title, label(s), state, date/time of closure, login of user who closed

class PullReqOverviewRoutineRequest(OnlineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, \
        username=None, password=None, token=None, keychain=None):
        super().__init__(repositoryURL, outputDirectory, \
            username=username, password=password, token=token, keychain=keychain)

class PullReqOverviewRoutine(OnlineRepositoryRoutine):

    def getRequestType(self):
        return PullReqOverviewRoutineRequest

    def githubImplementation(self, request, session):
        factory = DataEntityFactory()
        output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_PullReqOverview.csv".format(\
            outputDirectory=request.getOutputDirectory(), \
            repoName=request.getRepositoryLocation().getRepositoryName()))

        output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(self.__class__.__name__)
        output.setDateCreated(datetime.date.today())
        output.setURL(request.getRepositoryLocation().getURL())
        output.setColumnNames(["Pull Request ID", \
            "Date Created", \
            "Creator Login", \
            "Assignee Login(s)", \
            "Title of Pull Request", \
            "Number of Changed Files", \
            "Number of Commits", \
            "State of Pull Request", \
            "Date of Merge", \
            "Merger Login"])
        output.setColumnDatatypes(["str", \
            "str", \
            "str", \
            "str", \
            "str", \
            "str", \
            "str", \
            "str", \
            "str", \
            "str"])

        pulls = session.get_pulls(state="all")
        for pull in pulls:
            pullID = _replaceNoneWithEmptyString(\
                str(pull.id))
            datetimeCreated = _replaceNoneWithEmptyString(\
                str(get_time(pull.created_at)))
            creatorLogin = _replaceNoneWithEmptyString(\
                pull.user.login)
            assigneeList = [_replaceNoneWithEmptyString(user.login) \
                for user in pull.assignees]
            title = _replaceNoneWithEmptyString(\
                pull.title)
            filesChanged = _replaceNoneWithEmptyString(\
                str(pull.changed_files))
            pullCommits = _replaceNoneWithEmptyString(\
                str(pull.commits))
            pullState = _replaceNoneWithEmptyString(\
                pull.state)
            if pull.merged_at is not None:
                datetimeMerged = _replaceNoneWithEmptyString(\
                    str(get_time(pull.merged_at)))
            else:
                datetimeMerged = ""
            if pull.merged_by is not None:
                mergerLogin = _replaceNoneWithEmptyString(\
                    pull.merged_by.login)
            else:
                mergerLogin = ""

            output.addRecord([pullID, \
                datetimeCreated, \
                creatorLogin, \
                ";".join(assigneeList), \
                title, \
                filesChanged, \
                pullCommits, \
                pullState, \
                datetimeMerged, \
                mergerLogin])

        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(\
            message="PullReqOverviewRoutine completed!", attachments=output)

    def gitlabImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass

    def bitbucketImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass



# Routine to scrape natural language data from pull requests
#  Treats each "post" (i.e. original post and comments) as a separate entry
#  For each post, gets:
#   Unique issue ID (based on original post), type of post (original/comment),
#   date/time of creation, creator login, body text

class PullReqDetailsRoutineRequest(OnlineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, \
        username=None, password=None, token=None, keychain=None):
        super().__init__(repositoryURL, outputDirectory, \
            username=username, password=password, token=token, keychain=keychain)

class PullReqDetailsRoutine(OnlineRepositoryRoutine):

    def getRequestType(self):
        return PullReqDetailsRoutineRequest

    def githubImplementation(self, request, session):
        factory = DataEntityFactory()
        output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_PullReqDetails.csv".format(\
            outputDirectory=request.getOutputDirectory(), \
            repoName=request.getRepositoryLocation().getRepositoryName()))

        output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(self.__class__.__name__)
        output.setDateCreated(datetime.date.today())
        output.setURL(request.getRepositoryLocation().getURL())
        output.setColumnNames(["Issue ID of Original Post", \
            "Type of Post", \
            "Date Created", \
            "Creator Login", \
            "Body Text"])
        output.setColumnDatatypes(["str", \
            "str", \
            "str", \
            "str", \
            "str"])

        issues = session.get_issues(state="all")
        for issue in issues:
            issueID = _replaceNoneWithEmptyString(\
                str(issue.id))
            datetimeCreated = _replaceNoneWithEmptyString(\
                str(get_time(issue.created_at)))
            creatorLogin = _replaceNoneWithEmptyString(\
                issue.user.login)
            bodyText = _replaceNoneWithEmptyString(\
                issue.body)
            commentList = issue.get_comments()

            output.addRecord([issueID, \
                "original", \
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
                    "comment", \
                    datetimeCreated, \
                    creatorLogin, \
                    bodyText])

        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(\
            message="PullReqDetailsRoutine completed!", attachments=output)

    def gitlabImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass

    def bitbucketImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass
