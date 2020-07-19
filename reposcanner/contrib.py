from reposcanner.routines import OfflineRepositoryAnalysisRoutine,OnlineRepositoryAnalysisRoutine
from reposcanner.requests import OfflineRoutineRequest,OnlineRoutineRequest
from reposcanner.response import ResponseFactory
import pygit2

#import matplotlib.pyplot as plt
#import seaborn as sns
import time, datetime
#import statistics
import csv



class ContributionPeriodRoutineRequest(OfflineRoutineRequest):
        def __init__(self,repositoryURL,outputDirectory,workspaceDirectory):
                super().__init__(repositoryURL,outputDirectory,workspaceDirectory)

#TODO: Convert to new routine model.
class ContributionPeriodRoutine(OfflineRepositoryAnalysisRoutine):
        """
        Calculates the extents of code contribution periods of each contributor.
        """
        
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
                
        def render(self,request,response):
                pass

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
                                
#TODO: Convert to new routine model.                                
class ContributorListRoutine(OfflineRepositoryAnalysisRoutine):
        """
        Calculates the list of contributors and the number of lines contributed.
        """
        def execute(self):
                numberOfCommitsByContributor = {}
                
                for commit in self.repository.walk(self.repository.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
                        if commit.author.name not in numberOfCommitsByContributor:
                                numberOfCommitsByContributor[commit.author.name] = 1
                        else:
                                numberOfCommitsByContributor[commit.author.name] += 1
                        
                return numberOfCommitsByContributor
                
        def render(self,data):
                pass

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
 



class ContributorAccountListRoutineRequest(OnlineRoutineRequest):
        def __init__(self,repositoryURL,outputDirectory,username=None,password=None,token=None,keychain=None):
                super().__init__(repositoryURL,outputDirectory,username=username,password=password,token=token,keychain=keychain)

class ContributorAccountListRoutine(OnlineRepositoryAnalysisRoutine):
        """
        Contact the version control platform API, and get the account information of everyone who has ever contributed to the repository.
        """
        
        def canHandleRequest(self,request):
                if isinstance(request, ContributorAccountListRoutineRequest):
                        return True
                else:
                        return False
        
        def getRequestType(self):
                return ContributorAccountListRoutineRequest
                
        def _replaceNoneWithEmptyString(self,value):
                if value is None:
                        return ""
                else:
                        return value
        
        def githubImplementation(self,request,session):
                contributors = [contributor for contributor in session.get_contributors()]
                output = []
                for contributor in contributors:
                        entry = {}
                        entry["username"] = self._replaceNoneWithEmptyString(contributor.login)
                        entry["name"] = self._replaceNoneWithEmptyString(contributor.name)
                        entry["emails"] = [self._replaceNoneWithEmptyString(contributor.email)]
                        output.append(entry)
                
                responseFactory = ResponseFactory()
                return responseFactory.createSuccessResponse(
                        message="Completed!",attachments=output)
                
        def gitlabImplementation(self,request,session):
                contributors = [contributor for contributor in session.users.list()]
                output = []
                for contributor in contributors:
                        entry = {}
                        entry["username"] = contributor.username
                        entry["name"] = contributor.name
                        entry["emails"] = [user.emails.list()]
                        output.append(entry)
                responseFactory = ResponseFactory()
                return responseFactory.createSuccessResponse(
                        message="Completed!",attachments=output)
                
        #def bitbucketImplementation(self,request,session):
        #        pass
                
        def render(self,request,response):
                if not response.wasSuccessful():
                        return None
        
        def export(self,request,response):
                if not response.wasSuccessful():
                        return None
                contributors = response.getAttachments()
                today = datetime.datetime.now()
                
                with open('{outputDirectory}/{repoName}_contributorAccounts.csv'.format(
                        outputDirectory=request.getOutputDirectory(),repoName=request.getRepositoryLocation().getRepositoryName()),'w', newline='\n') as contributorAccountsFile:
                        
                        contributionWriter = csv.writer(contributorAccountsFile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        contributionWriter.writerow(["Date/Time of Analysis", "{dateOfAnalysis}".format(dateOfAnalysis=str(today))])
                        contributionWriter.writerow(["Repository", "{canonicalName}".format(canonicalName=request.getRepositoryLocation().getCanonicalName())])
                        
                        
                        contributionWriter.writerow([
                                "Login Name",
                                "Actual Name",
                                "Email(s)"
                        ])
                        
                        for contributor in contributors:
                                contributionWriter.writerow([contributor["username"],contributor["name"], ';'.join(contributor["emails"])])                       
                        

