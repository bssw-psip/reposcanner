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



# Routine to scrape data from GitHub Issues

class IssueTrackerRoutineRequest(OnlineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, \
        username=None, password=None, token=None, keychain=None):
        super().__init__(repositoryURL, outputDirectory, \
                username=username, password=password, token=token, keychain=keychain)

class IssueTrackerRoutine(OnlineRepositoryRoutine):

    def getRequestType(self):
        return IssueTrackerRoutineRequest

    def githubImplementation(self, request, session):
        def _replaceNoneWithEmptyString(value):
            if value is None:
                return ""
            else:
                return value

        factory = DataEntityFactory()
        output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_IssueTracker.csv".format(\
                outputDirectory=request.getOutputDirectory(), \
                repoName=request.getRepositoryLocation().getRepositoryName()))

        output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(self.__class__.__name__)
        output.setDateCreated(datetime.date.today())
        output.setURL(request.getRepositoryLocation().getURL())
        output.setColumnNames(["Date Created", \
                "Creator Login", \
                "Assignee Login(s)", \
                "Title of Issue", \
                "Body Text of Issue", \
                "Comment(s)"])
        output.setColumnDatatypes(["str", \
                "str", \
                "str", \
                "str", \
                "str", \
                "str"])

        issues = session.get_issues()
        for issue in issues:
            datetimeCreated = str(get_time(issue.created_at))
            creatorLogin = issue.user.login
            assigneeList = issue.assignees
            title = issue.title
            bodyText = issue.body

            # TODO:  Find a better way to organize comments in the csv output.
            #   Right now, this just lists all comments in a single cell, in the format
            #     [user] commented at time [time]:  [comment]
            #   with semicolons separating the info for different comments.
            #   It seems like there should be a better way to organize this, but since each
            #   issue has a different number of comments, what is it? Maybe make each post,
            #   including the original post and all subsequent comments, a different csv entry?
            #   And then label those entries with unique identifiers for each issue and tag as
            #   either "body text" or "comment text"?
            numberOfComments = issue.comments
            comments = issue.get_comments()
            commentsList = []
            for comment in comments:
                commentsList.append(\
                        comment.user.login + " commented at time " + \
                        str(get_time(comment.created_at)) + ":  " + \
                        comment.body)

            output.addRecord([_replaceNoneWithEmptyString(datetimeCreated), \
                    _replaceNoneWithEmptyString(creatorLogin), \
                    ";".join([_replaceNoneWithEmptyString(assignee.login) for assignee in assigneeList]), \
                    _replaceNoneWithEmptyString(title), \
                    _replaceNoneWithEmptyString(bodyText), \
                    ";".join([_replaceNoneWithEmptyString(comment) for comment in commentsList])])

        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(\
                message="IssueTrackerRoutine completed!", attachments=output)

    def gitlabImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass

    def bitbucketImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass

