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
#  Unique pull ID, date/time of creation,
#  creator login, assignee login(s), requested reviewer login(s),
#  title, number of files changed, number of commits, state,
#  branch to merge to, branch to merge from, date/time of merge,
#  login of user who merged

class PullRequestOverviewRoutineRequest(OnlineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, \
        username=None, password=None, token=None, keychain=None):
        super().__init__(repositoryURL, outputDirectory, \
            username=username, password=password, token=token, keychain=keychain)

class PullRequestOverviewRoutine(OnlineRepositoryRoutine):

    def getRequestType(self):
        return PullRequestOverviewRoutineRequest

    def githubImplementation(self, request, session):
        factory = DataEntityFactory()
        output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_PullRequestOverview.csv".format(\
            outputDirectory=request.getOutputDirectory(), \
            repoName=request.getRepositoryLocation().getRepositoryName()))

        output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(self.__class__.__name__)
        output.setDateCreated(datetime.date.today())
        output.setURL(request.getRepositoryLocation().getURL())
        output.setColumnNames(["Pull Request ID", \
            "Date Created", \
            "Creator Login", \
            "Assignee Logins", \
            "Requested Reviewer Logins"
            "Title of Pull Request", \
            "Number of Changed Files", \
            "Number of Commits", \
            "Branch to Merge From", \
            "Branch to Merge To", \
            "State of Pull Request", \
            "Date Merged", \
            "Merger Login"])
        output.setColumnDatatypes(["int", \
            "int", \
            "str", \
            "str", \
            "str", \
            "str", \
            "int", \
            "int", \
            "str", \
            "str", \
            "str", \
            "str", \
            "str"])

        pulls = session.get_pulls(state="all")
        for pull in pulls:
            pullID = pull.id
            datetimeCreated = get_time(pull.created_at)
            creatorLogin = _replaceNoneWithEmptyString(\
                pull.user.login)
            assigneeList = [_replaceNoneWithEmptyString(user.login) \
                for user in pull.assignees]
            reviewers = pull.get_review_requests()
            reviewerList = [_replaceNoneWithEmptyString(user.login) \
                for user in reviewers[0]]
            title = _replaceNoneWithEmptyString(\
                pull.title)
            if pull.changed_files is not None:
                filesChanged = pull.changed_files
            else:
                filesChanged = 0
            if pull.commits is not None:
                pullCommits = pull.commits
            else:
                pullCommits = 0
            mergeFrom = _replaceNoneWithEmptyString(\
                pull.head.label)
            mergeTo = _replaceNoneWithEmptyString(\
                pull.base.label)
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
                ";".join(reviewerList), \
                title, \
                filesChanged, \
                pullCommits, \
                mergeFrom, \
                mergeTo, \
                pullState, \
                datetimeMerged, \
                mergerLogin])

        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(\
            message="PullRequestOverviewRoutine completed!", attachments=output)

    def gitlabImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass

    def bitbucketImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass



# Routine to scrape natural language data from pull requests
#  Treats each "post" (i.e. original pull request and comments) as a separate entry
#  For each post, gets:
#   Unique issue ID (based on original post), type of post
#   (original pull request/issue comment/review comment/review),
#   date/time of creation, creator login, body text

class PullRequestDetailsRoutineRequest(OnlineRoutineRequest):
    def __init__(self, repositoryURL, outputDirectory, \
        username=None, password=None, token=None, keychain=None):
        super().__init__(repositoryURL, outputDirectory, \
            username=username, password=password, token=token, keychain=keychain)

class PullRequestDetailsRoutine(OnlineRepositoryRoutine):

    def getRequestType(self):
        return PullRequestDetailsRoutineRequest

    def githubImplementation(self, request, session):
        factory = DataEntityFactory()
        output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_PullRequestDetails.csv".format(\
            outputDirectory=request.getOutputDirectory(), \
            repoName=request.getRepositoryLocation().getRepositoryName()))

        output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(self.__class__.__name__)
        output.setDateCreated(datetime.date.today())
        output.setURL(request.getRepositoryLocation().getURL())
        output.setColumnNames(["Issue ID of Original Pull Request", \
            "Type of Post", \
            "Date Created", \
            "Creator Login", \
            "Body Text"])
        output.setColumnDatatypes(["int", \
            "str", \
            "int", \
            "str", \
            "str"])

        pulls = session.get_pulls(state="all")
        for pull in pulls:
            pullID = pull.id
            datetimeCreated = get_time(pull.created_at)
            creatorLogin = _replaceNoneWithEmptyString(\
                pull.user.login)
            bodyText = _replaceNoneWithEmptyString(\
                pull.body)

            output.addRecord([pullID, \
                "original pull request", \
                datetimeCreated, \
                creatorLogin, \
                bodyText])
            
            # TODO:  There's probably a more efficient way to combine the lists of
            #  issue comments, review comments, and reviews using the
            #  built-in pygithub class github.PaginatedList.PaginatedList,
            #  but this should suffice for now
            pullComments = []
            
            # Get the "conversation" comments on a pull request
            #  Pygithub calls these "issue comments"
            for comment in pull.get_issue_comments():
                datetimeCreated = get_time(comment.created_at)
                creatorLogin = _replaceNoneWithEmptyString(\
                    comment.user.login)
                bodyText = _replaceNoneWithEmptyString(\
                    comment.body)
                pullComments.append([pullID, \
                    "issue comment", \
                    datetimeCreated, \
                    creatorLogin, \
                    bodyText])
                
            # Get the in-line comments on specific lines of code in a pull request
            #  Pygithub calls these "review comments"
            for comment in pull.get_review_comments():
                datetimeCreated = get_time(comment.created_at)
                creatorLogin = _replaceNoneWithEmptyString(\
                    comment.user.login)
                bodyText = _replaceNoneWithEmptyString(\
                    comment.body)
                pullComments.append([pullID, \
                    "review comment", \
                    datetimeCreated, \
                    creatorLogin, \
                    bodyText])
                
            # Get the overall comments associated with a group of in-line comments
            #  Pygithub calls these "reviews"
            for comment in pull.get_reviews():
                datetimeCreated = get_time(comment.submitted_at)
                creatorLogin = _replaceNoneWithEmptyString(\
                    comment.user.login)
                bodyText = _replaceNoneWithEmptyString(\
                    comment.body)
                pullComments.append([pullID, \
                    "review", \
                    datetimeCreated, \
                    creatorLogin, \
                    bodyText])
                
            # Sort list of all comments by date of posting
            for comment in sorted(pullComments, key=lambda x: x[2]):
                output.addRecord(comment)

        output.writeToFile()
        responseFactory = ResponseFactory()
        return responseFactory.createSuccessResponse(\
            message="PullRequestDetailsRoutine completed!", attachments=output)

    def gitlabImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass

    def bitbucketImplementation(self, request, session):
        # TODO:  Implement IssueTrackerRoutine for GitLab
        pass
