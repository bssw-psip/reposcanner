import reposcanner.contrib as contrib
import reposcanner.data as data

def test_TeamSizeAndDistributionAnalysisRequest_isDirectlyConstructible():
        request = contrib.TeamSizeAndDistributionAnalysisRequest()
        

def test_TeamSizeAndDistributionAnalysisRequest_criteriaFunctionRecognizesNecessaryFiles():
        request = contrib.TeamSizeAndDistributionAnalysisRequest()
        
        dataEntityFactory = data.DataEntityFactory()
        fileA = dataEntityFactory.createAnnotatedCSVData("fileA.csv")
        fileB = dataEntityFactory.createAnnotatedCSVData("fileB.csv")
        fileC = dataEntityFactory.createAnnotatedCSVData("fileC.csv")
        irregularData = [5,6,7]
        
        fileA.setCreator("ContributorAccountListRoutine")
        fileB.setCreator("external")
        fileC.setCreator("UnrelatedRoutine")
        
        assert(request.criteriaFunction(fileA))
        assert(request.criteriaFunction(fileB))
        assert(not request.criteriaFunction(fileC))
        assert(irregularData)
        
def test_TeamSizeAndDistributionAnalysisRequest_fetchesDataFromStore():
        request = contrib.TeamSizeAndDistributionAnalysisRequest()
        
        dataEntityFactory = data.DataEntityFactory()
        fileA = dataEntityFactory.createAnnotatedCSVData("fileA.csv")
        fileB = dataEntityFactory.createAnnotatedCSVData("fileB.csv")
        fileC = dataEntityFactory.createAnnotatedCSVData("fileC.csv")
        irregularData = [5,6,7]
        
        fileA.setCreator("ContributorAccountListRoutine")
        fileB.setCreator("external")
        fileC.setCreator("UnrelatedRoutine")
        
        store = data.DataEntityStore()
        store.insert(fileA)
        store.insert(fileB)
        store.insert(fileC)
        store.insert(irregularData)
        
        assert(len(request.getData()) == 0)
        request.fetchDataFromStore(store)
        dataInsideRequest = request.getData()
        assert(len(dataInsideRequest) == 2)
        assert(fileA in dataInsideRequest)
        assert(fileB in dataInsideRequest)

        
def test_TeamSizeAndDistributionAnalysis_isDirectlyConstructible():
        analysis = contrib.TeamSizeAndDistributionAnalysis()
        
def test_TeamSizeAndDistributionAnalysis_requestTypeMatchesExpectedType():
        analysis = contrib.TeamSizeAndDistributionAnalysis()
        assert(analysis.getRequestType() == contrib.TeamSizeAndDistributionAnalysisRequest)
        request = contrib.TeamSizeAndDistributionAnalysisRequest()
        assert(analysis.canHandleRequest(request))
        
def test_TeamSizeAndDistributionAnalysis_analysisReturnsFailureResponseIfThereIsNoContributorDataAvailable():
        request = contrib.TeamSizeAndDistributionAnalysisRequest()
        store = data.DataEntityStore() #Store is empty! No data available to compute the analysis!
        request.fetchDataFromStore(store)
        analysis = contrib.TeamSizeAndDistributionAnalysis()
        assert(analysis.canHandleRequest(request))
        response = analysis.run(request)
        assert(not response.wasSuccessful())
        assert(response.hasMessage())
        assert(response.getMessage() == "Received no ContributorAccountListRoutine data.")
        
def test_TeamSizeAndDistributionAnalysis_analysisReturnsFailureResponseIfLoginDataNotAvailable():
        store = data.DataEntityStore()
        dataEntityFactory = data.DataEntityFactory()
        analysis = contrib.TeamSizeAndDistributionAnalysis()
        contributorAccountFile = dataEntityFactory.createAnnotatedCSVData("contrib_account_file.csv")
        contributorAccountFile.setCreator("ContributorAccountListRoutine")
        store.insert(contributorAccountFile)
        
        requestWithNoLoginData = contrib.TeamSizeAndDistributionAnalysisRequest()
        requestWithNoLoginData.fetchDataFromStore(store) #Store has contributor data, but no github_login.csv.
        
        noLoginDataResponse = analysis.run(requestWithNoLoginData)
        assert(not noLoginDataResponse.wasSuccessful())
        
def test_TeamSizeAndDistributionAnalysis_canHandleTestData(tmpdir):
        def generateContributorAccountListFile(store):
                dataEntityFactory = data.DataEntityFactory()
                contributorAccountFile = dataEntityFactory.createAnnotatedCSVData("data/contrib_account_file.csv")
                contributorAccountFile.setURL("https://www.github.com/scikit/scikit")
                contributorAccountFile.setCreator("ContributorAccountListRoutine")
                contributorAccountFile.setColumnNames(["Login Name","Actual Name","Email(s)"])
                contributorAccountFile.setColumnDatatypes(["str","str","str"])
                contributorAccountFile.addRecord(["jsmith","John Smith","jmsmith@llnl.gov"])
                contributorAccountFile.addRecord(["ajones","Alice Jones","alicejones@sandia.gov"])
                contributorAccountFile.addRecord(["mmson","Mark Markson","markmark@gmail.com"])  #Mark is a non-ECP third-party contributor.
                contributorAccountFile.addRecord(["jimthewizard","Jimothy Forrest","jforrest@lbl@gov"])
                store.insert(contributorAccountFile)
                
        def generateGithubLoginFile(store):
                dataEntityFactory = data.DataEntityFactory()
                githubLoginFile = dataEntityFactory.createAnnotatedCSVData("data/github_login.csv")
                githubLoginFile.setCreator("external")
                githubLoginFile.addRecord(["GID","login","FID"])
                githubLoginFile.addRecord([0,"jsmith",2342])
                githubLoginFile.addRecord([1,"ajones",3320])
                githubLoginFile.addRecord([2,"mmson",10002])
                githubLoginFile.addRecord([2,"jimthewizard",138])
                store.insert(githubLoginFile)
                
        def generateECPMembersFile(store):
                dataEntityFactory = data.DataEntityFactory()
                membersFile = dataEntityFactory.createAnnotatedCSVData("data/members.csv")
                membersFile.setCreator("external")
                membersFile.addRecord(["MID","FID","IID","IID2","PID","role"])
                membersFile.addRecord([5,2342,1,None,8,None])
                membersFile.addRecord([11,3320,2,10,8,None]) #Alice is both a Sandian and a professor at a university.
                membersFile.addRecord([50,138,3,None,13,None])
                store.insert(membersFile)
        
        store = data.DataEntityStore()

        generateContributorAccountListFile(store)
        generateGithubLoginFile(store)
        generateECPMembersFile(store)
        
        mockOutputDirectory = tmpdir.mkdir("./mockoutput/")
        request = contrib.TeamSizeAndDistributionAnalysisRequest(outputDirectory=mockOutputDirectory)
        request.fetchDataFromStore(store)
        
        analysis = contrib.TeamSizeAndDistributionAnalysis()
        response = analysis.run(request)
        assert(response.wasSuccessful())
        
        csvOutput = response.getAttachments()[0]
        assert(csvOutput.getCreator() == "TeamSizeAndDistributionAnalysis") 
        scikitEntry = csvOutput.getRawRecords()[0]
        print(scikitEntry)
        assert(scikitEntry[0] == 'https://www.github.com/scikit/scikit') #The data came from the scikit repository.
        assert(scikitEntry[1] == 4) #There were four contributors to the repository.
        assert(scikitEntry[2] == 3) #Three of the contributors are known ECP members.
        assert(scikitEntry[3] == 4) #The three contributors are representative of four different institutions (one contributor has two institutional affiliations).
        
        
        
        
        
        