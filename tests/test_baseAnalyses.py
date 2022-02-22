import pytest
from reposcanner.git import GitEntityFactory
import reposcanner.analyses as analyses
import reposcanner.requests as requests
import reposcanner.response as responses

def test_DataAnalysis_isConstructibleWithMockImplementation(mocker):
        mocker.patch.multiple(analyses.DataAnalysis,__abstractmethods__=set())
        genericAnalysis = analyses.DataAnalysis()
        
def test_DataAnalysis_runCanReturnResponse(mocker):
        mocker.patch.multiple(analyses.DataAnalysis,__abstractmethods__=set())
        def executeGeneratesResponse(self,request):
                factory = responses.ResponseFactory()
                response = factory.createSuccessResponse()
                return response
        analyses.DataAnalysis.execute = executeGeneratesResponse
        genericAnalysis = analyses.DataAnalysis()
        genericRequest = requests.AnalysisRequestModel(outputDirectory="./")
        response = genericAnalysis.run(genericRequest)
        assert(response.wasSuccessful())
        
def test_DataAnalysis_exportCanAddAttachments(mocker):
        mocker.patch.multiple(analyses.DataAnalysis,__abstractmethods__=set())
        def executeGeneratesResponse(self,request):
                factory = responses.ResponseFactory()
                response = factory.createSuccessResponse(attachments=[])
                response.addAttachment("data")
                return response
        
        analyses.DataAnalysis.execute = executeGeneratesResponse
        genericAnalysis = analyses.DataAnalysis()
        genericRequest = requests.AnalysisRequestModel(outputDirectory="./")
        response = genericAnalysis.run(genericRequest)
        assert(response.wasSuccessful())
        assert(response.hasAttachments())
        assert(len(response.getAttachments()) == 1)
        
def test_DataAnalysis_canSetConfigurationParameters(mocker):
        mocker.patch.multiple(analyses.DataAnalysis,__abstractmethods__=set())
        genericAnalysis = analyses.DataAnalysis()
        configurationParameters = {"verbose" : True, "debug" : False}
        assert(not genericAnalysis.hasConfigurationParameters())
        assert(genericAnalysis.getConfigurationParameters() == None)
        genericAnalysis.setConfigurationParameters(configurationParameters)
        assert(genericAnalysis.hasConfigurationParameters())
        assert(genericAnalysis.getConfigurationParameters() == configurationParameters)