import pytest
import reposcanner.data as data
import datetime

def test_AnnotatedCSVData_isDirectlyConstructible():
        dataEntity = data.AnnotatedCSVData("test.csv")
        
def test_AnnotatedCSVData_isConstructibleByFactory():
        factory = data.DataEntityFactory()
        factory.createAnnotatedCSVData("test.csv")
        
def test_AnnotatedCSVData_canGetFilePath():
        dataEntity = data.AnnotatedCSVData("test.csv")
        assert(dataEntity.getFilePath() == "test.csv")
        
def test_AnnotatedCSVData_canGetKeysForMetadataAfterConstruction():
        dataEntity = data.AnnotatedCSVData("test.csv")
        keys = dataEntity.getAttributeKeys()
        assert("creator" in keys)
        assert("datecreated" in keys)
        assert("projectid" in keys)
        assert("projectname" in keys)
        assert("url" in keys)
        assert("names" in keys)
        assert("datatypes" in keys)
        
def test_AnnotatedCSVData_validationOfMetadataFailsInitially():
        dataEntity = data.AnnotatedCSVData("test.csv")
        assert(not dataEntity.validateMetadata())
        
def test_AnnotatedCSVData_canStoreAndValidateMetadata():
        dataEntity = data.AnnotatedCSVData("test.csv")
        timestamp = datetime.datetime.now()
        columnNames = ["contributor","numberOfCommits"]
        columnDatatypes = ["str","int"]
        
        dataEntity.setCreator("routine")
        dataEntity.setDateCreated(timestamp)
        dataEntity.setProjectID("ABC552")
        dataEntity.setProjectName("QuantumSorcery")
        dataEntity.setURL("https://www.github.com/quantsci/quantumsorcery/")
        dataEntity.setColumnNames(columnNames)
        dataEntity.setColumnDatatypes(columnDatatypes)
        
        assert(dataEntity.getCreator() == "routine")
        assert(dataEntity.getDateCreated() == timestamp)
        assert(dataEntity.getProjectID() == "ABC552")
        assert(dataEntity.getProjectName() == "QuantumSorcery")
        assert(dataEntity.getURL() == "https://www.github.com/quantsci/quantumsorcery/")
        assert(dataEntity.getColumnNames() == columnNames)
        assert(dataEntity.getColumnDatatypes() == columnDatatypes)
        
        assert(dataEntity.validateMetadata())
        
def test_AnnotatedCSVData_initiallyHasNoRecords():
        dataEntity = data.AnnotatedCSVData("test.csv")
        assert(len(dataEntity.getRawRecords()) == 0)
        
def test_AnnotatedCSVData_canProduceRecordDictionaries():
        dataEntity = data.AnnotatedCSVData("test.csv")
        columnNames = ["contributor","numberOfCommits"]
        dataEntity.setColumnNames(columnNames)
        dataEntity.addRecord(["johnsmith",552])
        
        rawRecords = dataEntity.getRawRecords()
        assert(len(rawRecords) == 1)
        rawRecord = rawRecords[0]
        assert(rawRecord[0] == "johnsmith")
        assert(rawRecord[1] == 552)
        
        recordDictionaries = dataEntity.getRecordsAsDicts()
        assert(len(recordDictionaries) == 1)
        entry = recordDictionaries[0]
        assert("contributor" in entry)
        assert(entry["contributor"] == "johnsmith")
        assert("numberOfCommits" in entry)
        assert(entry["numberOfCommits"] == 552)
        
        
        
        