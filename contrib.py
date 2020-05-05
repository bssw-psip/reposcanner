from routines import *

#import matplotlib.pyplot as plt
#import seaborn as sns
import time, datetime
#import statistics
import csv

class ContributionPeriodRoutine(OfflineRepositoryAnalysisRoutine):
        """
        Calculates the extents of code contribution periods of each contributor.
        """
        def __init__(self,repositoryName,localRepoDirectory,outputDirectory):
                super().__init__(repositoryName=repositoryName,localRepoDirectory=localRepoDirectory,outputDirectory=outputDirectory)
        
        def execute(self):
                contributors = []
                numberOfCommitsByContributor = {}
                timestampsByContributor = {}          
                
                for commit in self.repository.walk(self.repository.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
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
                                
                                
class ContributorListRoutine(OfflineRepositoryAnalysisRoutine):
        """
        Calculates the list of contributors and the number of lines contributed.
        """
        #def __init__(self,repositoryName,localRepoDirectory,outputDirectory):
        #        super().__init__(repositoryName=repositoryName,localRepoDirectory=localRepoDirectory,outputDirectory=outputDirectory)
        
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
                                
                                
class ContributorList(OnlineRepositoryAnalysisRoutine):
    def execute(self):
        pass
    def render(self, data):
        pass
    def export(self, data):
        pass


