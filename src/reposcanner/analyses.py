from abc import ABC, abstractmethod


class DataAnalysis(ABC):
    """The abstract base class for all data analyses. Methods cover
    the execution of analyses, rendering, and exporting of data."""

    def canHandleRequest(self, request):
        """
        Returns True if the routine is capable of handling the request (i.e. the
        RequestModel is of the type that the analysis expects), and False otherwise.
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
    def execute(self, request):
        """
        Contains the code for processing data generated by mining routines and/or from external
        databases.

        Parameters:
                request (@input): A RequestModel object that encapsulates all the information needed
                to run the analysis.

        """
        pass

    def run(self, request):
        """
        Encodes the workflow of a DataAnalysis object. The client only needs
        to run this method in order to get results.
        """
        response = self.execute(request)
        return response

    def hasConfigurationParameters(self):
        """
        Checks whether the analysis object was passed configuration parameters,
        whether valid or not. Routines are not required to do anything with parameters
        that are passed to them via the config file.
        """
        try:
            parameters = self.configParameters
            return parameters is not None
        except BaseException:
            return False

    def getConfigurationParameters(self):
        """
        Returns the configuration parameters assigned to the analysis.
        """
        try:
            parameters = self.configParameters
            return parameters
        except BaseException:
            return None

    def setConfigurationParameters(self, configParameters):
        """
        Assigns configuration parameters to a newly created analysis.
        """
        self.configParameters = configParameters
