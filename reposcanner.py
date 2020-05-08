from git import GitHubCredentials, RepositoryName, pygitAvailable, pygithubAvailable
import argparse, os
from contrib import ContributionPeriodRoutine, ContributorAccountListRoutine
from growth import GrowthRoutine

def scannerMain(args):
        """
        The master routine for Reposcanner.
        """
        if args.enableLocalAnalyses is True and not pygitAvailable:
                args.enableLocalAnalyses = False
        if args.enableOnlineAnalyses is True and not pygithubAvailable:
                args.enableOnlineAnalyses = False
        
        credentials = GitHubCredentials(username=args.username,password=args.password,token=args.token)
        repositoryName = RepositoryName(combinedString=args.repo)
        
        if not os.path.exists(args.outputDirectory):
                raise OSError("Reposcanner couldn't find the specified output directory. Shutting down as a precaution.")
        
        
        args = dict(repositoryName=repositoryName,
                    localRepoDirectory=args.localRepoDirectory,
                    credentials=credentials,
                    outputDirectory=args.outputDirectory)
        contributionPeriodRoutine = ContributionPeriodRoutine(**args)
        contributionPeriodRoutine.run()
        #growthRoutine = GrowthRoutine(**args)
        #growthRoutine.run()
        accountListRoutine = ContributorAccountListRoutine(**args)
        accountListRoutine.run()

if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='The IDEAS-ECP PSIP Team Repository Scanner. Note: To use this tool for online PyGitHub-based analyses, you must supply either a username and password or an access token to communicate with the GitHub API.')
        parser.add_argument('--repo', action='store', type=str, help='The canonical name of the GitHub repository we want to study (expected form: owner/repoName).')
        parser.add_argument('--username',action='store',type=str,default=None,help='The username of the account used to talk to the GitHub API.')
        parser.add_argument('--password',action='store',type=str,default=None,help='The password of the account used to talk to the GitHub API.')
        parser.add_argument('--token',action='store',type=str,default=None,help='The token of the account used to talk to the GitHub API.')
        parser.add_argument('--outputDirectory',action='store',type=str,default='./',help='The path where we should output files. By default this is done in the directory from which this script is run.')
        parser.add_argument('--enableOnlineAnalyses', help='Set this flag to allow the reposcanner to perform analyses which require the tool to talk to the GitHub API. This clone will be cleaned up at termination.')
        parser.add_argument('--enableLocalAnalyses', help='Set this flag to allow the reposcanner to perform analyses which require the tool to make a clone of the repository. This clone will be removed at termination.')
        parser.add_argument('--localRepoDirectory',action='store',type=str,default='./temporary_repo_clone',help='If you want reposcanner to perform certain analyses that require a local clone of the repository, then it must have a location where it can clone the repository. By default this is done in the directory from which this script is run.')
        args = parser.parse_args()
        scannerMain(args)
        
