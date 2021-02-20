from reposcanner.routines import OfflineRepositoryRoutine,OnlineRepositoryRoutine
from reposcanner.requests import OfflineRoutineRequest,OnlineRoutineRequest
from reposcanner.response import ResponseFactory
from reposcanner.provenance import ReposcannerRunInformant
from reposcanner.data import DataEntityFactory
import pygit2

import time, datetime
import csv






        
"""
class ContributionPeriodRoutineRequest(OfflineRoutineRequest):
        def __init__(self,repositoryURL,outputDirectory,workspaceDirectory):
                super().__init__(repositoryURL,outputDirectory,workspaceDirectory)
"""

"""
class ContributionPeriodRoutine(OfflineRepositoryRoutine):
        
        #Calculates the extents of code contribution periods of each contributor.
        
        
        def canHandleRequest(self,request):
                if isinstance(request, ContributionPeriodRoutineRequest):
                        return True
                else:
                        return False
                        
        def getRequestType(self):
                return ContributionPeriodRoutineRequest
        
        def offlineImplementation(self,request,session):
                contributors = []
                numberOfCommitsByContributor = {}
                timestampsByContributor = {}      
                
                for commit in session.walk(session.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
                        if commit.author.name not in contributors:
                                contributors.append(commit.author.name)
                        
                        if commit.author.name not in numberOfCommitsByContributor:
                                numberOfCommitsByContributor[commit.author.name] = 1
                        else:
                                numberOfCommitsByContributor[commit.author.name] += 1
                        
                        timeOfCommit = commit.commit_time
                        
                        if commit.author.name not in timestampsByContributor:
                                timestampsByContributor[commit.author.name] = (timeOfCommit,timeOfCommit)
                        else:
                                firstCommit,latestCommit = timestampsByContributor[commit.author.name]
                                if timeOfCommit < firstCommit:
                                        timestampsByContributor[commit.author.name] = (timeOfCommit,latestCommit)
                                if timeOfCommit > latestCommit:
                                        timestampsByContributor[commit.author.name] = (firstCommit,timeOfCommit)
                        
                return contributors,numberOfCommitsByContributor,timestampsByContributor

        def export(self,request,response):
                contributors,numberOfCommitsByContributor,timestampsByContributor = data
                
                today = datetime.datetime.now()
                
                with open('{outputDirectory}/{repoName}_contributionPeriods.csv'.format(
                        outputDirectory=self.outputDirectory,repoName=self.repositoryName.getRepositoryName()),'w', newline='\n') as contributionPeriodsFile:
                        
                        contributionWriter = csv.writer(contributionPeriodsFile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        
                        contributionWriter.writerow(["Date/Time of Analysis", "{dateOfAnalysis}".format(dateOfAnalysis=str(today))])
                        contributionWriter.writerow(["Repository", "{canonicalName}".format(canonicalName=self.repositoryName.getCanonicalName())])
                        
                        contributionWriter.writerow([
                                "Contributor Name",
                                "Number of Commits By Contributor",
                                "Timestamp of First Commit",
                                "Timestamp of Last Commit",
                                "Length of Contribution Period (In Days)",
                                "Has Made a Commit in the Past 365 Days"
                        ])
                        contributionPeriodsInDays = { contributor : ((timestampsByContributor[contributor][1] - timestampsByContributor[contributor][0]) / 60 / 60 / 24) for contributor in timestampsByContributor }
                        for contributor in contributors:
                                contributorName = contributor
                                numberOfCommits = numberOfCommitsByContributor[contributor]
                                firstCommitTimestamp,lastCommitTimestamp = timestampsByContributor[contributor]
                                contributionPeriod = numberOfCommitsByContributor[contributor]
                                
                                activeInPastYear = ((today.timestamp() - lastCommitTimestamp) / 60 / 60 / 24) <= 365
                                
                                contributionWriter.writerow([contributorName,numberOfCommits,firstCommitTimestamp,lastCommitTimestamp,contributionPeriod,activeInPastYear])
"""

"""                              
class ContributorListRoutine(OfflineRepositoryRoutine):
        #Calculates the list of contributors and the number of lines contributed.
        def execute(self):
                numberOfCommitsByContributor = {}
                
                for commit in self.repository.walk(self.repository.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
                        if commit.author.name not in numberOfCommitsByContributor:
                                numberOfCommitsByContributor[commit.author.name] = 1
                        else:
                                numberOfCommitsByContributor[commit.author.name] += 1
                        
                return numberOfCommitsByContributor


        def export(self,data):
                contributors,numberOfCommitsByContributor,timestampsByContributor = data
                
                today = datetime.datetime.now()
                
                with open('{outputDirectory}/{repoName}_contributionPeriods.csv'.format(
                        outputDirectory=self.outputDirectory,repoName=self.repositoryName.getRepositoryName()),'w', newline='\n') as contributionPeriodsFile:
                        
                        contributionWriter = csv.writer(contributionPeriodsFile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        
                        contributionWriter.writerow(["Date/Time of Analysis", "{dateOfAnalysis}".format(dateOfAnalysis=str(today))])
                        contributionWriter.writerow(["Repository", "{canonicalName}".format(canonicalName=self.repositoryName.getCanonicalName())])
                        
                        contributionWriter.writerow([
                                "Contributor Name",
                                "Number of Commits By Contributor",
                                "Timestamp of First Commit",
                                "Timestamp of Last Commit",
                                "Length of Contribution Period (In Days)",
                                "Has Made a Commit in the Past 365 Days"
                        ])
                        contributionPeriodsInDays = { contributor : ((timestampsByContributor[contributor][1] - timestampsByContributor[contributor][0]) / 60 / 60 / 24) for contributor in timestampsByContributor }
                        for contributor in contributors:
                                contributorName = contributor
                                numberOfCommits = numberOfCommitsByContributor[contributor]
                                firstCommitTimestamp,lastCommitTimestamp = timestampsByContributor[contributor]
                                contributionPeriod = numberOfCommitsByContributor[contributor]
                                
                                activeInPastYear = ((today.timestamp() - lastCommitTimestamp) / 60 / 60 / 24) <= 365
                                
                                contributionWriter.writerow([contributorName,numberOfCommits,firstCommitTimestamp,lastCommitTimestamp,contributionPeriod,activeInPastYear])
"""


class OfflineCommitCountsRoutineRequest(OfflineRoutineRequest):
        def __init__(self,repositoryURL,outputDirectory,workspaceDirectory):
                super().__init__(repositoryURL,outputDirectory,workspaceDirectory)

class OfflineCommitCountsRoutine(OfflineRepositoryRoutine):
        """
        This routine clones a repository and calculates the total number of commits associated with the
        emails of contributors.
        """
        
        def getRequestType(self):
                return OfflineCommitCountsRoutineRequest
        
        def offlineImplementation(self,request,session):
                numberOfCommitsByContributor = {}
                
                for commit in session.repository.walk(session.repository.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
                        if commit.author.email not in numberOfCommitsByContributor:
                                numberOfCommitsByContributor[commit.author.email] = 1
                        else:
                                numberOfCommitsByContributor[commit.author.email] += 1
                        
                factory = DataEntityFactory()
                output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_offlineCommitCounts.csv".format(
                        outputDirectory=request.getOutputDirectory(),
                        repoName=request.getRepositoryLocation().getRepositoryName()))
                        
                output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
                output.setCreator(self.__class__.__name__)
                output.setDateCreated(datetime.date.today())
                output.setURL(request.getRepositoryLocation().getURL())
                output.setColumnNames(["email","commitCount"])
                output.setColumnDatatypes(["str","int"])
                
                for emailAddress in numberOfCommitsByContributor:
                        output.addRecord([
                                emailAddress,
                                numberOfCommitsByContributor[emailAddress]
                                ])
                output.writeToFile()
                responseFactory = ResponseFactory()
                return responseFactory.createSuccessResponse(message="Completed!",attachments=output)
                        
                



class ContributorAccountListRoutineRequest(OnlineRoutineRequest):
        def __init__(self,repositoryURL,outputDirectory,username=None,password=None,token=None,keychain=None):
                super().__init__(repositoryURL,outputDirectory,username=username,password=password,token=token,keychain=keychain)

class ContributorAccountListRoutine(OnlineRepositoryRoutine):
        """
        Contact the version control platform API, and get the account information of everyone who has ever contributed to the repository.
        """
        
        def getRequestType(self):
                return ContributorAccountListRoutineRequest
                
        def _replaceNoneWithEmptyString(self,value):
                if value is None:
                        return ""
                else:
                        return value
        
        def githubImplementation(self,request,session):                
                factory = DataEntityFactory()
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
                                self._replaceNoneWithEmptyString(contributor.login),
                                self._replaceNoneWithEmptyString(contributor.name),
                                ';'.join([self._replaceNoneWithEmptyString(contributor.email)])
                                
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
                
        #def bitbucketImplementation(self,request,session):
        #        pass             
                        

