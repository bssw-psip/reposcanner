from abc import ABC, abstractmethod
import urllib3
import os
import pygit2
from reposcanner.git import GitEntityFactory,RepositoryLocation
from reposcanner.response import ResponseFactory

class DataMiningRoutine(ABC):
        """
        The abstract base class for all data mining routines.
        """
        def canHandleRequest(self,request):
                """
                Returns True if the routine is capable of handling the request (i.e. the
                RequestModel is of the type that the routine expects), and False otherwise.
                """
                if isinstance(request, self.getRequestType()):
                        return True
                else:
                        return False

        @abstractmethod
        def getRequestType(self):
                """
                Returns the class object for the routine's companion request type.
                """
                pass

        @abstractmethod
        def execute(self,request):
                """
                Contains the code for executing the data mining operations.

                Parameters:
                        request (@input): A RequestModel object that encapsulates all the information needed
                        to run the routine.
                """
                pass
        
        def run(self,request):
                """
                Encodes the workflow of a DataMiningRoutine object. The client only needs
                to run this method in order to get results.
                """
                response = self.execute(request)
                return response

class RepositoryRoutine(DataMiningRoutine):
        """The abstract base class for all software repository analysis routines."""
        pass
                
class ExternalCommandLineToolRoutine(DataMiningRoutine):
        """
        Abstract base class for routines that call other command-line tools to mine data.
        Having calls to external tools handled within Reposcanner allows us to provide consistent
        provenance for their use.
        """
        @abstractmethod
        def isExternalToolAvailable(self):
            """
            Checks to see whether the tool can be called on the command-line.
            This method should return True if so, False if not.
            """
            pass


class OfflineRepositoryRoutine(RepositoryRoutine):
        """
        Class that encapsulates the stages of a PyGit2-based analysis procedure operating on a clone of a repository.
        """
        def __init__(self):
                pass


        def execute(self,request):
                """
                The Offline routine execute() method delegates responsibility for performing the routine to
                the offlineImplementation() method. Subclasses of this class are responsible for
                overriding that methods.
                """
                responseFactory = ResponseFactory()
                if not self.canHandleRequest(request):
                        return responseFactory.createFailureResponse(
                        message="The routine was passed a request of the wrong type.")
                elif request.hasErrors():
                        return responseFactory.createFailureResponse(
                        message="The request had errors in it and cannot be processed.",
                        attachments=request.getErrors())
                else:
                        try:
                                if not os.path.exists(request.getCloneDirectory()):
                                    def init_remote(repo, name, url):
                                        # Create the remote with a mirroring url
                                        remote = repo.remotes.create(name, url, "+refs/heads/*:refs/heads/*")
                                        # And set the configuration option to true for the push command
                                        #mirror_var = "remote.{}.mirror".format(name)
                                        #repo.config[mirror_var] = True
                                        # Return the remote, which pygit2 will use to perform the clone
                                        return remote
                                    session = pygit2.clone_repository(request.getRepositoryLocation().getURL(),
                                                                      request.getCloneDirectory(),
                                                                      bare=True,
                                                                      remote=init_remote)
                                else:
                                    session = pygit2.Repository(request.getCloneDirectory())

                                return self.offlineImplementation(request=request,session=session)

                        except Exception as e:
                                return responseFactory.createFailureResponse(
                                    message="OfflineRepositoryRoutine Encountered an unexpected exception ({etype}).".format(etype=type(e)),
                                    attachments=[e])

        def offlineImplementation(self,request,session):
                """
                This method should contain the GitHub API implementation of the routine.
                By default, it'll return a failure response. Subclasses are responsible for
                overriding this method.

                request: An OfflineRoutineRequest object.
                session: A pygit2 Repository object.
                """
                responseFactory = ResponseFactory()
                return responseFactory.createFailureResponse(
                        message="This routine has no implementation available"
                        "to handle an offline clone of a repository.")


class OnlineRepositoryRoutine(RepositoryRoutine):
        """
        Class that encapsulates the stages of an PyGitHub-based analysis procedure operating on the GitHub API.
        """

        def __init__(self):
                factory = GitEntityFactory()
                compositeCreator = factory.createVCSAPISessionCompositeCreator()
                githubCreator = factory.createGitHubAPISessionCreator()
                gitlabCreator = factory.createGitlabAPISessionCreator()
                compositeCreator.addChild(githubCreator)
                compositeCreator.addChild(gitlabCreator)
                self._sessionCreator = compositeCreator

        def execute(self,request):
                """
                The Online routine execute() method delegates responsibility for performing the routine to
                platform-API-specific methods. Subclasses of this class are responsible for
                overriding those methods.
                """
                responseFactory = ResponseFactory()
                if not self.canHandleRequest(request):
                        return responseFactory.createFailureResponse(
                        message="The routine was passed a request of the wrong type.")
                elif request.hasErrors():
                        return responseFactory.createFailureResponse(
                        message="The request had errors in it and cannot be processed.",
                        attachments=request.getErrors())
                elif not self._sessionCreator.canHandleRepository(request.getRepositoryLocation()):
                        return responseFactory.createFailureResponse(
                        message="The routine's VCS API session creator is not able "
                        "to handle the platform of the repository ({platform}).".format(
                                platform=request.getRepositoryLocation().getVersionControlPlatform()))
                else:
                        platform = request.getRepositoryLocation().getVersionControlPlatform()
                        repositoryLocation = request.getRepositoryLocation()
                        credentials = request.getCredentials()
                        try:
                                if platform == RepositoryLocation.VersionControlPlatform.GITHUB:
                                        return self.githubImplementation(request=request,
                                                session=self._sessionCreator.connect(repositoryLocation,credentials))
                                elif platform == RepositoryLocation.VersionControlPlatform.GITLAB:
                                        return self.gitlabImplementation(request=request,
                                                session=self._sessionCreator.connect(repositoryLocation,credentials))
                                elif platform == RepositoryLocation.VersionControlPlatform.BITBUCKET:
                                        return self.bitbucketImplementation(request=request,
                                                session=self._sessionCreator.connect(repositoryLocation,credentials))
                                else:
                                        return responseFactory.createFailureResponse(
                                                message="The platform of the repository is \
                                                not supported by this routine ({platform}).".format(
                                                platform=platform))
                        except Exception as e:
                                return responseFactory.createFailureResponse(
                                    message="OnlineRepositoryRoutine Encountered an unexpected exception.",
                                    attachments=[e])

        @property
        def sessionCreator(self):
                """We expose this attribute for testing/validation purposes. Normally
                the session creator isn't touched after construction."""
                return self._sessionCreator

        @sessionCreator.setter
        def sessionCreator(self, sessionCreator):
                """We expose this attribute for testing/validation purposes. Normally
                the session creator isn't touched after construction."""
                self._sessionCreator = sessionCreator


        def githubImplementation(self,request,session):
                """
                This method should contain the GitHub API implementation of the routine.
                By default, it'll return a failure response. Subclasses are responsible for
                overriding this method.

                request: An OnlineRoutineRequest object.
                session: An API session provided by a VCSAPISessionCompositeCreator.
                """
                responseFactory = ResponseFactory()
                return responseFactory.createFailureResponse(
                        message="This routine has no implementation available \
                        to handle a GitHub repository.")

        def gitlabImplementation(self,request,session):
                """
                This method should contain the GitHub API implementation of the routine.
                By default, it'll return a failure response. Subclasses are responsible for
                overriding this method.

                request: An OnlineRoutineRequest object.
                session: An API session provided by a VCSAPISessionCompositeCreator.
                """
                responseFactory = ResponseFactory()
                return responseFactory.createFailureResponse(
                        message="This routine has no implementation available \
                        to handle a Gitlab repository.")


        def bitbucketImplementation(self,request,session):
                """
                This method should contain the GitHub API implementation of the routine.
                By default, it'll return a failure response. Subclasses are responsible for
                overriding this method.

                request: An OnlineRoutineRequest object.
                session: An API session provided by a VCSAPISessionCompositeCreator.
                """
                responseFactory = ResponseFactory()
                return responseFactory.createFailureResponse(
                        message="This routine has no implementation available \
                        to handle a Bitbucket repository.")
                        


