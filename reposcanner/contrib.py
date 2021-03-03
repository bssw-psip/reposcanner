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

#import matplotlib.pyplot as plt
#import seaborn as sns






        
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
                
                for commit in session.walk(session.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
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
        #TODO: ContributorAccountListRoutine lacks a bitbucketImplementation(self,request,session) method.
        
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
                

class TeamSizeAndDistributionAnalysisRequest(AnalysisRequestModel):
        def criteriaFunction(self,entity):
                """
                Here we assume that the entity is, in fact, a
                ReposcannerDataEntity. Because we haven't yet
                decided to enforce a restriction such that only
                ReposcannerDataEntity objects can be stored by
                a DataEntityStore, we'll wrap it in a try block.
                We may revisit this decision later.
                """
                try:
                        creator = entity.getCreator()
                        if creator == "ContributorAccountListRoutine" or creator == "external":
                                return True
                        else:
                                return False
                        
                except AttributeError as e:
                        return False
                        

class TeamSizeAndDistributionAnalysis(DataAnalysis):
        """
        This analysis examines the number of contributors to each repository and
        the distribution of those contributors across institutions to get a sense
        for the scope and scale of a software project.
        
        Output from this analysis includes Matplotlib/Seaborn graphs describing
        the data, and a CSV file containing the data used to generate those graphs.
        """      
        def getRequestType(self):
                """
                Returns the class object for the routine's companion request type.
                """
                return TeamSizeAndDistributionAnalysisRequest
        
        def execute(self,request):
                responseFactory = ResponseFactory()
                
                data = request.getData()
                contributorListEntities = [ entity for entity in data if entity.getCreator() == "ContributorAccountListRoutine" ]
                if len(contributorListEntities) == 0:
                        return responseFactory.createFailureResponse(message="Received no ContributorAccountListRoutine data.")
                
                loginData = next((entity for entity in data if "github_login.csv" in entity.getFilePath()), None)
                if loginData == None:
                        return responseFactory.createFailureResponse(message="Failed to find github_login.csv from reposcanner-data.")
                else:
                        loginData = loginData.getDataFrame(firstRowContainsHeaders=True)
                        
                memberData = next((entity for entity in data if "members.csv" in entity.getFilePath()), None)
                if memberData == None:
                        return responseFactory.createFailureResponse(message="Failed to find members.csv from reposcanner-data.")
                else:
                        memberData = memberData.getDataFrame(firstRowContainsHeaders=True)
                
                dataEntityFactory = DataEntityFactory()
                analysisCSVOutput = dataEntityFactory.createAnnotatedCSVData("{outputDirectory}/TeamSizeAndDistributionAnalysis_results.csv".format(
                        outputDirectory=request.getOutputDirectory()))
                
                analysisCSVOutput.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
                analysisCSVOutput.setCreator(self.__class__.__name__)
                analysisCSVOutput.setDateCreated(datetime.date.today())
                analysisCSVOutput.setColumnNames(["URL","numberOfContributors","numberOfKnownECPContributors","numberOfInstitutionsInvolved"])
                analysisCSVOutput.setColumnDatatypes(["str","int","int","int"])
                
                for contributorListEntity in contributorListEntities:
                        contributorListFrame = contributorListEntity.getDataFrame()
                        
                        repositoryURL = contributorListEntity.getURL()
                        numberOfContributors = len(contributorListFrame.index)
                        numberOfKnownECPContributors = 0
                        institutionIDsInvolved = set()
                        
                        for index, individualContributor in contributorListFrame.iterrows():
                                if individualContributor["Login Name"] in loginData["login"].values:
                                        folksID = loginData.loc[loginData['login'] == individualContributor["Login Name"]]['FID'].values[0]
                                        
                                        if folksID in memberData['FID'].values: 
                                                numberOfKnownECPContributors += 1
                                                ecpMemberEntry = memberData.loc[memberData['FID'] == folksID]
                                                
                                                
                                                #Note: Though the vast majority of ECP members belong to only one institution, it is
                                                #possible for a member to belong to more than one (e.g. simultaneously holding a position
                                                #at a national lab and a university).
                                                firstInstitutionOfECPMember = ecpMemberEntry['IID'].values[0]
                                                secondInstitutionOfECPMember = ecpMemberEntry['IID2'].values[0]
                                                if firstInstitutionOfECPMember is not None and not np.isnan(firstInstitutionOfECPMember):
                                                        institutionIDsInvolved.add(firstInstitutionOfECPMember)
                                                if secondInstitutionOfECPMember is not None and not np.isnan(secondInstitutionOfECPMember):
                                                        institutionIDsInvolved.add(secondInstitutionOfECPMember)
                        
                        analysisCSVOutput.addRecord([repositoryURL,numberOfContributors,numberOfKnownECPContributors,len(institutionIDsInvolved)])
                
                analysisCSVOutput.writeToFile()
                
                return responseFactory.createSuccessResponse(message="Completed!",attachments=analysisCSVOutput)
                                                
                                
                                
                                
                                        
                                
                                
                                
                        
                        
                    
                        
                         
                
                
