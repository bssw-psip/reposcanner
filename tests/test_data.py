from pathlib import Path
import pytest
import reposcanner.data as data
import datetime
import pathlib


def test_AnnotatedCSVData_isDirectlyConstructible() -> None:
    dataEntity = data.AnnotatedCSVData("test.csv")


def test_AnnotatedCSVData_isConstructibleByFactory() -> None:
    factory = data.DataEntityFactory()
    factory.createAnnotatedCSVData("test.csv")


def test_AnnotatedCSVData_canGetFilePath() -> None:
    dataEntity = data.AnnotatedCSVData("test.csv")
    assert(dataEntity.getFilePath() == Path("test.csv"))


def test_AnnotatedCSVData_canGetKeysForMetadataAfterConstruction() -> None:
    dataEntity = data.AnnotatedCSVData("test.csv")
    keys = dataEntity.getAttributeKeys()
    assert("creator" in keys)
    assert("datecreated" in keys)
    assert("projectid" in keys)
    assert("projectname" in keys)
    assert("url" in keys)
    assert("names" in keys)
    assert("datatypes" in keys)


def test_AnnotatedCSVData_validationOfMetadataFailsInitially() -> None:
    dataEntity = data.AnnotatedCSVData("test.csv")
    assert(not dataEntity.validateMetadata())


def test_AnnotatedCSVData_canStoreAndValidateMetadata() -> None:
    dataEntity = data.AnnotatedCSVData("test.csv")
    timestamp = datetime.date.today()
    columnNames = ["contributor", "numberOfCommits"]
    columnDatatypes = ["str", "int"]

    dataEntity.setReposcannerExecutionID("19m397b")
    dataEntity.setCreator("routine")
    dataEntity.setDateCreated(timestamp)
    dataEntity.setProjectID("ABC552")
    dataEntity.setProjectName("QuantumSorcery")
    dataEntity.setURL("https://www.github.com/quantsci/quantumsorcery/")
    dataEntity.setColumnNames(columnNames)
    dataEntity.setColumnDatatypes(columnDatatypes)

    assert(dataEntity.getReposcannerExecutionID() == "19m397b")
    assert(dataEntity.getCreator() == "routine")
    assert(dataEntity.getDateCreated() == timestamp)
    assert(dataEntity.getProjectID() == "ABC552")
    assert(dataEntity.getProjectName() == "QuantumSorcery")
    assert(dataEntity.getURL() == "https://www.github.com/quantsci/quantumsorcery/")
    assert(dataEntity.getColumnNames() == columnNames)
    assert(dataEntity.getColumnDatatypes() == columnDatatypes)

    assert(dataEntity.validateMetadata())


def test_AnnotatedCSVData_initiallyHasNoRecords() -> None:
    dataEntity = data.AnnotatedCSVData("test.csv")
    assert(len(dataEntity.getRawRecords()) == 0)


def test_AnnotatedCSVData_canProduceRecordDictionaries() -> None:
    dataEntity = data.AnnotatedCSVData("test.csv")
    columnNames = ["contributor", "numberOfCommits"]
    dataEntity.setColumnNames(columnNames)
    dataEntity.addRecord(["johnsmith", 552])

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


def test_AnnotatedCSVData_canConvertToDataFrame() -> None:
    dataEntity = data.AnnotatedCSVData("test.csv")
    columnNames = ["contributor", "numberOfCommits"]
    dataEntity.setColumnNames(columnNames)
    dataEntity.addRecord(["johnsmith", 552])
    dataEntity.addRecord(["alicejones", 231])
    dataEntity.addRecord(["carolcarson", 77])
    frame = dataEntity.getDataFrame()
    assert(frame["contributor"][0] == "johnsmith")
    assert(frame["contributor"][1] == "alicejones")
    assert(frame["contributor"][2] == "carolcarson")
    assert(frame["numberOfCommits"][0] == 552)
    assert(frame["numberOfCommits"][1] == 231)
    assert(frame["numberOfCommits"][2] == 77)


def test_AnnotatedCSVData_canConvertToDataFrameFromFileWithFirstRowHeader() -> None:
    dataEntity = data.AnnotatedCSVData("test.csv")
    dataEntity.addRecord(["contributor", "numberOfCommits"])
    dataEntity.addRecord(["johnsmith", 552])
    dataEntity.addRecord(["alicejones", 231])
    dataEntity.addRecord(["carolcarson", 77])
    frame = dataEntity.getDataFrame(firstRowContainsHeaders=True)
    assert(frame["contributor"][0] == "johnsmith")
    assert(frame["contributor"][1] == "alicejones")
    assert(frame["contributor"][2] == "carolcarson")
    assert(frame["numberOfCommits"][0] == 552)
    assert(frame["numberOfCommits"][1] == 231)
    assert(frame["numberOfCommits"][2] == 77)


def test_AnnotatedCSVData_canStoreDataToDisk(tmp_path: pathlib.Path) -> None:
    filePath = tmp_path / "csvtest.csv"
    dataEntity = data.AnnotatedCSVData(filePath)
    timestamp = datetime.date.today()
    columnNames = ["contributor", "numberOfCommits"]
    columnDatatypes = ["str", "int"]

    dataEntity.setReposcannerExecutionID("19m397b")
    dataEntity.setCreator("routine")
    dataEntity.setDateCreated(timestamp)
    dataEntity.setProjectID("ABC552")
    dataEntity.setProjectName("QuantumSorcery")
    dataEntity.setURL("https://www.github.com/quantsci/quantumsorcery/")
    dataEntity.setColumnNames(columnNames)
    dataEntity.setColumnDatatypes(columnDatatypes)
    assert(dataEntity.validateMetadata())

    dataEntity.addRecord(["johnsmith", 552])

    assert(not dataEntity.fileExists())
    dataEntity.writeToFile()
    assert(dataEntity.fileExists())

    dataEntityB = data.AnnotatedCSVData(filePath)
    dataEntityB.readFromFile()
    assert(dataEntityB.getReposcannerExecutionID() == "19m397b")
    assert(dataEntityB.getCreator() == "routine")
    assert(dataEntityB.getDateCreated() == timestamp)
    assert(dataEntityB.getProjectID() == "ABC552")
    assert(dataEntityB.getProjectName() == "QuantumSorcery")
    assert(dataEntityB.getURL() == "https://www.github.com/quantsci/quantumsorcery/")
    assert(dataEntityB.getColumnNames() == columnNames)
    assert(dataEntityB.getColumnDatatypes() == columnDatatypes)
    assert(dataEntityB.validateMetadata())


def test_YAMLData_isDirectlyConstructible() -> None:
    dataEntity = data.YAMLData("test.yaml")


def test_AnnotatedYAMLData_isConstructibleByFactory() -> None:
    factory = data.DataEntityFactory()
    factory.createYAMLData("test.yaml")


def test_YAMLData_initiallyHoldsNoData() -> None:
    dataEntity = data.YAMLData("test.yaml")
    assert(len(dataEntity.getData()) == 0)


def test_YAMLData_canReadDataFromDisk(tmp_path: pathlib.Path) -> None:
    filePath = tmp_path / "test.yaml"

    with open(filePath, 'w') as outfile:
        contents = """
                ADTR02:
                  name: IDEAS Productivity
                  urls:
                  - https://github.com/bssw-psip/ptc-catalog
                  - https://github.com/bssw-psip/practice-guides
                  - https://github.com/bssw-psip/bssw-psip.github.io
                """
        outfile.write(contents)
    dataEntity = data.YAMLData(filePath)
    dataEntity.readFromFile()
    dataDict = dataEntity.getData()
    assert('ADTR02' in dataDict)
    assert('name' in dataDict['ADTR02'] and dataDict['ADTR02']
           ['name'] == 'IDEAS Productivity')
    assert('urls' in dataDict['ADTR02'] and len(dataDict['ADTR02']['urls']) == 3)


def test_YAMLData_canStoreDataToDisk(tmp_path: pathlib.Path) -> None:
    filePath = tmp_path / "test.yaml"
    dataEntity = data.YAMLData(filePath)
    dataDict = {
        'ADTR02': {
            'name': 'IDEAS Productivity',
            'urls': [
                'https://github.com/bssw-psip/ptc-catalog',
                'https://github.com/bssw-psip/practice-guides',
                'https://github.com/bssw-psip/bssw-psip.github.io']}}
    dataEntity.setData(dataDict)
    dataEntity.writeToFile()

    dataEntityB = data.YAMLData(filePath)
    dataEntityB.readFromFile()
    dataDictB = dataEntityB.getData()
    assert('ADTR02' in dataDictB)
    assert('name' in dataDictB['ADTR02']
           and dataDictB['ADTR02']['name'] == 'IDEAS Productivity')
    assert('urls' in dataDictB['ADTR02'] and len(dataDictB['ADTR02']['urls']) == 3)


def test_YAMLData_canSupportNestedParametersForMiningRoutineConfigurations(
        tmp_path: pathlib.Path) -> None:
    sub = tmp_path
    filePath = sub / "config.yaml"

    with open(filePath, 'w') as outfile:
        contents = """
                routines:
                    - ContributorAccountListRoutine
                    - ExternalToolRoutine:
                        toolConfig: toolConfigFile.config
                        readonly: True
                        verbose: False
                    - AnotherRepositoryMiningRoutine
                """
        outfile.write(contents)
    dataEntity = data.YAMLData(filePath)
    dataEntity.readFromFile()
    dataDict = dataEntity.getData()
    assert('routines' in dataDict)
    assert('ContributorAccountListRoutine' in dataDict['routines'])
    assert('ExternalToolRoutine' in dataDict['routines'][1])
    assert(dataDict['routines'][1]['ExternalToolRoutine']
           ['toolConfig'] == 'toolConfigFile.config')
    assert(dataDict['routines'][1]['ExternalToolRoutine']['readonly'])
    assert(dataDict['routines'][1]['ExternalToolRoutine']['verbose'] == False)


def test_DataEntityStore_isDirectlyConstructible() -> None:
    store = data.DataEntityStore()


def test_DataEntityStore_isInitiallyEmpty() -> None:
    store = data.DataEntityStore()
    assert(len(store) == 0)


def test_DataEntityStore_canInsertAndRemoveEntities() -> None:
    store = data.DataEntityStore()

    entityA = data.YAMLData("repositories.yaml")
    entityB = data.AnnotatedCSVData("routineresults.csv")

    store.insert(entityA)
    assert(entityA in store)
    assert(len(store) == 1)

    store.insert(entityB)
    assert(entityB in store)
    assert(len(store) == 2)

    store.remove(entityB)
    assert(entityB not in store)
    assert(len(store) == 1)

    store.remove(entityA)
    assert(entityA not in store)
    assert(len(store) == 0)


def test_DataEntityStore_canReadOverAllEntities() -> None:
    store = data.DataEntityStore()

    for i in range(20):
        entity = data.AnnotatedCSVData("routineresults{i}.csv".format(i=i))
        store.insert(entity)

    numberOfEntitiesInStore = 0
    for _ in store.read():
        numberOfEntitiesInStore += 1
    assert(numberOfEntitiesInStore == 20)


def test_DataEntityStore_canFilterByCriteria() -> None:
    commitCountsA = data.AnnotatedCSVData("commitcounts_a.csv")
    commitCountsB = data.AnnotatedCSVData("commitcounts_b.csv")
    commitCountsC = data.AnnotatedCSVData("commitcounts_c.csv")

    commitCountsA.setCreator("CommitCountRoutine")
    commitCountsB.setCreator("CommitCountRoutine")
    commitCountsC.setCreator("CommitCountRoutine")
    commitCountsA.setURL("https://github.com/Super-Net/SNet")
    commitCountsB.setURL("https://gitlab.com/TeamSciKit/SciKit")
    commitCountsC.setURL("https://bitbucket.com/Ligre/AdAstra")

    contributorListA = data.AnnotatedCSVData("contributorlist_a.csv")
    contributorListB = data.AnnotatedCSVData("contributorlist_b.csv")
    contributorListC = data.AnnotatedCSVData("contributorlist_c.csv")

    contributorListA.setCreator("ContributorListRoutine")
    contributorListB.setCreator("ContributorListRoutine")
    contributorListC.setCreator("ContributorListRoutine")
    contributorListA.setURL("https://github.com/Super-Net/SNet")
    contributorListB.setURL("https://gitlab.com/TeamSciKit/SciKit")
    contributorListC.setURL("https://bitbucket.com/Ligre/AdAstra")

    store = data.DataEntityStore()
    store.insert(commitCountsA)
    store.insert(commitCountsB)
    store.insert(commitCountsC)
    store.insert(contributorListA)
    store.insert(contributorListB)
    store.insert(contributorListC)

    def criteria_OnlyCommitCounts(entity: data.ReposcannerDataEntity) -> bool:
        return entity.getCreator() == "CommitCountRoutine"

    onlyCommitCounts = store.getByCriteria(criteria_OnlyCommitCounts)
    assert(len(onlyCommitCounts) == 3)

    def criteria_OnlyAdAstraRelated(entity: data.ReposcannerDataEntity) -> bool:
        return (isinstance(entity, data.AnnotatedCSVData)
            and entity.getURL() == "https://bitbucket.com/Ligre/AdAstra")

    onlyAdAstraRelated = store.getByCriteria(criteria_OnlyAdAstraRelated)
    assert(len(onlyAdAstraRelated) == 2)
