from reposcanner.routines import OfflineRepositoryRoutine,OnlineRepositoryRoutine
from reposcanner.analyses import DataAnalysis
from reposcanner.requests import OfflineRoutineRequest,OnlineRoutineRequest,AnalysisRequestModel
from reposcanner.response import ResponseFactory
from reposcanner.provenance import ReposcannerRunInformant
from reposcanner.data import DataEntityFactory
import pygit2

from pathlib import Path
import time, datetime, re, csv
import pandas as pd
import numpy as np

#import matplotlib.pyplot as plt
#import seaborn as sns

########################################


class CommitInfoMiningRoutineRequest(OfflineRoutineRequest):
        def __init__(self,repositoryURL,outputDirectory,workspaceDirectory):
                super().__init__(repositoryURL,outputDirectory,workspaceDirectory)

class CommitInfoMiningRoutine(OfflineRepositoryRoutine):
        """
        This routine clones a repository and extracts information about each commit, including
        authorship information, the commit message, and which files were interacted with.
        """
        def getRequestType(self):
            return CommitInfoMiningRoutineRequest

        def offlineImplementation(self,request,session):

            factory = DataEntityFactory()
            fout = Path(request.getOutputDirectory()) \
                     / "{repoOwner}_{repoName}_CommitInfoMining.csv".format(
                         repoOwner=request.getRepositoryLocation().getOwner(),
                         repoName=request.getRepositoryLocation().getRepositoryName())

            output = factory.createAnnotatedCSVData(fout)

            responseFactory = ResponseFactory()
            if output.fileExists():
                output.readFromFile()
                return responseFactory.createSuccessResponse(message="[CommitInfoMiningRoutine] File already exists, \
                skipping...",attachments=output)


            output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
            output.setCreator(self.__class__.__name__)
            output.setDateCreated(datetime.date.today())
            output.setURL(request.getRepositoryLocation().getURL())


            output.setColumnNames(["commitHash","commitTime","authorEmail","authorName","authorTime",
                "committerEmail","committerName","committerTime","coauthors",
                "insertions", "deletions", "filesChanged","namesOfFilesChanged","commitMessage"])
            output.setColumnDatatypes(["str"]*8 + ["list"] + ["int"]*3 + ["list"] + ["str"])

            def _getFilesTouched(commit):
                #TODO: Go back and check this method. Are we correctly interpreting the semantics of
                #the deltas we receive from pygit2?
                changes = []
                if len(commit.parents) == 0:
                    diff = commit.tree.diff_to_tree()
                    # consider using "for fname in list(diff): (fname.delta.new_file.path, fname.line_stats)"
                    for delta in diff.deltas:
                        if delta.old_file.path not in changes and delta.old_file.path is not None:
                            changes.append(delta.old_file.path)
                        if delta.new_file.path not in changes and delta.new_file.path is not None:
                            changes.append(delta.new_file.path)
                else:
                    for parent in commit.parents:
                        diff = parent.tree.diff_to_tree(commit.tree)
                        for delta in diff.deltas:
                            if delta.old_file.path not in changes and delta.old_file.path is not None:
                                changes.append(delta.old_file.path)
                            if delta.new_file.path not in changes and delta.new_file.path is not None:
                                changes.append(delta.new_file.path)
                return changes

            def _cleanCommitMessage(s):
                #This replaces all sequences of whitespace characters
                #with a single space, eliminating tabs, newlines, etc.
                #Also get rid of commas, as commas are our default delimiter.
                return re.sub('\s+',' ',s).replace(',',' ')

            def _getStats(commit):
                changes = {'ins': 0, 'del': 0, 'files': 0}
                if len(commit.parents) == 0:
                    diff = commit.tree.diff_to_tree()
                    diff.find_similar() # handle renamed files
                    changes['ins'] += diff.stats.insertions
                    changes['del'] += diff.stats.deletions
                    changes['files'] += diff.stats.files_changed
                else:
                    for parent in commit.parents:
                        diff = parent.tree.diff_to_tree(commit.tree)
                        diff.find_similar()
                        changes['ins'] += diff.stats.insertions
                        changes['del'] += diff.stats.deletions
                        changes['files'] += diff.stats.files_changed
                return changes

            def _replaceNoneWithEmptyString(value):
                if value is None:
                    return ""
                else:
                    return value

            for commit in session.walk(session.head.target, pygit2.GIT_SORT_TIME | pygit2.GIT_SORT_TOPOLOGICAL):
                extractedCommitData = {}

                #The person who originally made the change and when they made it, a pygit2.Signature.
                author = commit.author
                authorEmail = author.email
                authorName = author.name
                authorTime = author.time #Unix timestamp, as in the number of seconds since midnight, 1 January 1970.

                #The person who submitted the commit and when they did so, a pygit2.Signature (can be different than author!).
                committer = commit.committer
                committerEmail = committer.email
                committerName = committer.name
                committerTime = committer.time #Unix timestamp, as in the number of seconds since midnight, 1 January 1970.

                #The SHA hash of the commit, a string. This is guaranteed to be unique for any commit in a given repo.
                #It is not guaranteed to be unique across commits from different repos, but in practice
                #hash collisions are *extremely* rare.
                commitHash = commit.hex

                #The time when the commit was applied to the repo, which should be the same as the committer's timestamp (?).
                commitTime = commit.commit_time

                #A message describing what changes were made to the repo by the commit, a string.
                # parse lines like:
                # Co-authored-by: Mystery Committer <mystery@predictivestatmech.org>
                commitMessage = commit.message

                coAuthors = []
                for line in commit.message.split('\n'):
                    m = re.match("\s*Co-authored-by: (.*)", line)
                    if m is not None:
                        coAuthors.append(m[1].strip())

                #All the files interacted with according to the tree associated with the commit.
                #filesTouched = _getFilesTouched(commit)
                changes = _getStats(commit)

                filesTouched = _getFilesTouched(commit)

                output.addRecord([_replaceNoneWithEmptyString(commitHash),
                    _replaceNoneWithEmptyString(commitTime),
                    _replaceNoneWithEmptyString(authorEmail),
                    _replaceNoneWithEmptyString(authorName),
                    _replaceNoneWithEmptyString(authorTime),
                    _replaceNoneWithEmptyString(committerEmail),
                    _replaceNoneWithEmptyString(committerName),
                    _replaceNoneWithEmptyString(committerTime),
                    ";".join(coAuthors),
                    changes['ins'], changes['del'], changes['files'],
                    ';'.join(filesTouched),
                    _cleanCommitMessage(_replaceNoneWithEmptyString(commitMessage))
                    ])

            output.writeToFile()
            return responseFactory.createSuccessResponse(
                    message="CommitInfoMiningRoutine completed!",attachments=output)



class OnlineCommitAuthorshipRoutineRequest(OnlineRoutineRequest):
        def __init__(self,repositoryURL,outputDirectory,username=None,password=None,token=None,keychain=None):
                super().__init__(repositoryURL,outputDirectory,username=username,password=password,token=token,keychain=keychain)

class OnlineCommitAuthorshipRoutine(OnlineRepositoryRoutine):
        """
        This routine traverses the commits for a given repository and associates each commit
        with GitHub/Gitlab/Bitbucket account information.
        """
        def getRequestType(self):
            return OnlineCommitAuthorshipRoutineRequest

        def githubImplementation(self,request,session):
            def _replaceNoneWithEmptyString(value):
                if value is None:
                    return ""
                else:
                    return value

            factory = DataEntityFactory()
            output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_OnlineCommitAuthorship.csv".format(
                    outputDirectory=request.getOutputDirectory(),
                    repoName=request.getRepositoryLocation().getRepositoryName()))

            output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
            output.setCreator(self.__class__.__name__)
            output.setDateCreated(datetime.date.today())
            output.setURL(request.getRepositoryLocation().getURL())
            output.setColumnNames(["commitHash","authorLogin","committerLogin"])
            output.setColumnDatatypes(["str","str","str"])

            commits = session.get_commits()
            for commit in commits:
                commitHash = commit.sha
                if commit.author is not None:
                    authorLogin = commit.author.login
                else:
                    authorLogin = None

                if commit.committer is not None:
                    committerLogin = commit.committer.login
                else:
                    committerLogin = None

                output.addRecord([_replaceNoneWithEmptyString(commitHash),
                    _replaceNoneWithEmptyString(authorLogin),
                    _replaceNoneWithEmptyString(committerLogin)])

            output.writeToFile()
            responseFactory = ResponseFactory()
            return responseFactory.createSuccessResponse(
                message="OnlineCommitAuthorshipRoutine completed!",attachments=output)


        def gitlabImplementation(self,request,session):
            def _replaceNoneWithEmptyString(value):
                if value is None:
                    return ""
                else:
                    return value

            factory = DataEntityFactory()
            output = factory.createAnnotatedCSVData("{outputDirectory}/{repoName}_OnlineCommitAuthorship.csv".format(
                    outputDirectory=request.getOutputDirectory(),
                    repoName=request.getRepositoryLocation().getRepositoryName()))

            output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
            output.setCreator(self.__class__.__name__)
            output.setDateCreated(datetime.date.today())
            output.setURL(request.getRepositoryLocation().getURL())
            output.setColumnNames(["commitHash","authorLogin","committerLogin"])
            output.setColumnDatatypes(["str","str","str"])

            #Note from Reed: As of July 2021 looks like there's no way to directly the username associated with a commit
            #via the Gitlab API, though this feature may be added in the future (see https://gitlab.com/gitlab-org/gitlab/-/issues/20924)
            #Instead, we can get the list of users and their associated emails, and map author/committer identities to Gitlab user accounts.
            users = [users for users in session.users.list()]
            mapOfEmailsToGitlabLogins = {}
            for user in users:
                #Gitlab users can have multiple email addresses, but no two users
                # can have the exact same email addresses.
                for email in user.emails.list():
                    mapOfEmailsToGitlabLogins[email] = user.username

            commits = session.commits.list()
            for commit in commits:
                commitHash = commit.id
                if commit.author_name is not None and commit.author_name in mapOfEmailsToGitlabLogins:
                    authorLogin = mapOfEmailsToGitlabLogins[commit.author_name]
                else:
                    authorLogin = None

                if commit.committer_name is not None and commit.committer_name in mapOfEmailsToGitlabLogins:
                    committerLogin = mapOfEmailsToGitlabLogins[commit.committer_name]
                else:
                    committerLogin = None

                output.addRecord([_replaceNoneWithEmptyString(commitHash),
                    _replaceNoneWithEmptyString(authorLogin),
                    _replaceNoneWithEmptyString(committerLogin)])

            output.writeToFile()
            responseFactory = ResponseFactory()
            return responseFactory.createSuccessResponse(
                message="OnlineCommitAuthorshipRoutine completed!",attachments=output)

        def bitbucketImplementation(self,request,session):
            #TODO: Implement Commit Author Identification Routine implementation for Gitlab.
            pass


class GambitCommitAuthorshipInferenceAnalysisRequest(AnalysisRequestModel):
        def criteriaFunction(self,entity):
                try:
                        creator = entity.getCreator()
                        if creator == "CommitInfoMiningRoutine":
                                return True
                        else:
                                return False

                except AttributeError as e:
                        return False

class GambitCommitAuthorshipInferenceAnalysis(DataAnalysis):
    """
    This routine provides an alternative way of assigning unique identities
    to authors in commit logs that does not require interacting with online platform APIs.
    Gambit (gambit-disambig) is an open-source name disambiguation tool for version control
    systems that became available following ICSE 2021 and was developed by Christoph Gote and
    Christian Zingg. It uses a rule-based approach to resolve author identities based
    on names and emails in commit logs.

    GambitCommitAuthorshipInferenceAnalysis will produce a CSV file mapping all unique
    name and email pairs among OnlineCommitAuthorshipRoutine outputs to unique author IDs.

    For details, see...
        https://github.com/gotec/gambit
        https://arxiv.org/pdf/2103.05666.pdf

    """

    def __init__(self):
        """
        We check for the presence of the (optional) gambit package. This analysis
        cannot run unless gambit-disambig is installed.
        """
        super(GambitCommitAuthorshipInferenceAnalysis, self).__init__()
        try:
            import gambit
        except ImportError:
            self.gambitIsAvailable = False
            self.gambitImportRef = None
        else:
            self.gambitIsAvailable = True
            self.gambitImportRef = gambit

    def getRequestType(self):
        """
        Returns the class object for the routine's companion request type.
        """
        return GambitCommitAuthorshipInferenceAnalysisRequest

    def execute(self,request):

        responseFactory = ResponseFactory()
        if not self.gambitIsAvailable:
            return responseFactory.createFailureResponse(message="Gambit is not \
            installed, halting execution.")

        data = request.getData()
        commitLogEntities = [entity for entity in data if entity.getCreator() == "CommitInfoMiningRoutine"]

        factory = DataEntityFactory()
        output = factory.createAnnotatedCSVData("{outputDirectory}/gambitAuthorIdentities.csv".format(
            outputDirectory=request.getOutputDirectory()))

        output.setReposcannerExecutionID(ReposcannerRunInformant().getReposcannerExecutionID())
        output.setCreator(self.__class__.__name__)
        output.setDateCreated(datetime.date.today())
        output.setColumnNames(["alias_name","alias_email","name","email","first_name",
            "last_name","penultimate_name","email_base","author_id"])
        output.setColumnDatatypes(["str"]*8+["int"])

        contributorNamesAndEmails = set()

        for commitLogEntity in commitLogEntities:
            commitLogFrame = commitLogEntity.getDataFrame()
            #TODO: Add support for co-authors listed in commit messages. We now collect this data
            #when running CommitInfoMiningRoutine, but we aren't yet checking it here.
            for index, row in commitLogFrame.iterrows():
                author = (row["authorName"],row["authorEmail"])
                committer = (row["committerName"],row["committerEmail"])
                if author not in contributorNamesAndEmails:
                    contributorNamesAndEmails.add(author)
                if committer not in contributorNamesAndEmails:
                    contributorNamesAndEmails.add(committer)

        # Create the pandas DataFrame to pass to gambit.
        contributorFrame = pd.DataFrame(contributorNamesAndEmails,columns = ['alias_name', 'alias_email'])


        gambitResult = self.gambitImportRef.disambiguate_aliases(contributorFrame)
        for index, row in gambitResult.iterrows():
            output.addRecord([
                row["alias_name"],
                row["alias_email"],
                row["name"],
                row["email"],
                row["first_name"],
                row["last_name"],
                row["penultimate_name"],
                row["email_base"],
                row["author_id"]])

        output.writeToFile()
        return responseFactory.createSuccessResponse(message="GambitCommitAuthorshipInferenceAnalysis \
        completed!",attachments=output)





class VerifiedCommitAuthorshipAnalysisRequest(AnalysisRequestModel):
        def criteriaFunction(self,entity):
                try:
                        creator = entity.getCreator()
                        if creator == "OnlineCommitAuthorshipRoutine" or creator == "CommitInfoMiningRoutine":
                                return True
                        else:
                                return False

                except AttributeError as e:
                        return False

class VerifiedCommitAuthorshipAnalysis(DataAnalysis):
        def getRequestType(self):
                """
                Returns the class object for the routine's companion request type.
                """
                return VerifiedCommitAuthorshipAnalysisRequest
        def execute(self,request):
                #TODO: Set up Verified Commit Authorship Analysis.
                pass

########################################

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

class FileInteractionRoutineRequest(OfflineRoutineRequest):
        def __init__(self,repositoryURL,outputDirectory,workspaceDirectory):
                super().__init__(repositoryURL,outputDirectory,workspaceDirectory)


class FileInteractionRoutine(OfflineRepositoryRoutine):
        def getRequestType(self):
                return FileInteractionRoutineRequest

        def offlineImplementation(self,request,session):
                #TODO: Implement offline, commit-based file interaction routine (in the vein of Vasilescu et al.).
                pass




class ContributorFileInteractionAnalysisRequest(AnalysisRequestModel):
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
                        if creator == "CommitAuthorIdentificationRoutine" or creator == "FileInteractionRoutine":
                                return True
                        else:
                                return False

                except AttributeError as e:
                        return False

class ContributorFileInteractionAnalysis(DataAnalysis):
        def getRequestType(self):
                """
                Returns the class object for the routine's companion request type.
                """
                return ContributorFileInteractionAnalysisRequest
        def execute(self,request):
                #TODO: Set up the Contributor File Interaction Analysis
                pass


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
