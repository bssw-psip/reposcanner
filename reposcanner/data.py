from abc import ABC, abstractmethod
import csv,re,os,hashlib
import datetime

class DataEntityFactory:
        def createAnnotatedCSVData(self,filePath):
                return AnnotatedCSVData(filePath=filePath)

class ReposcannerDataEntity(ABC):
        """
        Abstract base class for data objects that are created and/or used
        by Reposcanner and its mining routines and analyses.
        """
        
        def __init__(self,filePath):
                """
                filepath: The path to the file where the data will be written (or read from).
                metadataAttributes: metadata associated with the data entity.
                """
                self._metadataAttributes = {}
                self._filePath = filePath
                self.setReposcannerExecutionID(None)
                self.setDateCreated(None)
                self.setCreator(None)
             
        def getFilePath(self):
                return self._filePath
        
        def setMetadataAttribute(self,key,value):
                self._metadataAttributes[key] = value
                
        def getMetadataAttribute(self,key):
                return self._metadataAttributes[key]
                
        def getAttributeKeys(self):
                return self._metadataAttributes.keys()
                
        def setReposcannerExecutionID(self,executionid):
                """
                executionid: A string containing an id that uniquely identifies
                the particular run of the Reposcanner tool that was used to
                generate the data held by this data entity.
                """
                self.setMetadataAttribute("executionid",executionid)
                
        def getReposcannerExecutionID(self):
                return self.getMetadataAttribute("executionid")
                
        def setDateCreated(self,date):
                """
                datetime: A datetime.date object.
                """
                self.setMetadataAttribute("datecreated",date)
         
        def getDateCreated(self):
                return self.getMetadataAttribute("datecreated")
        
        def setCreator(self,creator):
                """
                creator: A string indicating what routine, analysis, etc.
                was responsible for creating this data entity.
                """
                self.setMetadataAttribute("creator",creator)
                
        def getCreator(self):
                return self.getMetadataAttribute("creator")
                
        def fileExists(self):
                return os.path.exists(self._filePath)
                
        def getMD5Hash(self):
                """
                Compute the MD5 checksum for a file for provenance-tracking purposes.
                """
                return hashlib.md5(self._filePath).hexdigest()  
        
        @abstractmethod      
        def validateMetadata(self):
                """
                Should hold routines that validate that all necessary
                metadata is provided and/or is accurate 
                (e.g. in the case of datatypes). Returns True or False.
                """
                pass
        
        @abstractmethod
        def readFromFile(self):
                """
                Load the data in the file. Data will be accessible via
                this object. 
                """
                pass
                
        @abstractmethod
        def writeToFile(self):
                """
                Write data held by this object to the file.
                """
                pass
                

class AnnotatedCSVData(ReposcannerDataEntity):
        """
        This data entity class represents a CSV file annotated with metadata.
        Getters/setters are provided for the metadata that 
        
        The embedded metadata format we use is consistent with W3C guidelines. 
        (Model for Tabular Data and Metadata on the Web, section 5.4).
        """
        
        def __init__(self,filePath):
                super().__init__(filePath)
                self._records = []
                self.setColumnNames([])
                self.setColumnDatatypes([])
                self.setProjectID(None)
                self.setProjectName(None)
                self.setURL(None)
        
        def setProjectID(self,projectid):
                """
                projectid: A string containing the idea for the project ID associated
                with a repository
                """
                self.setMetadataAttribute("projectid",projectid)
        
        def getProjectID(self):
                return self.getMetadataAttribute("projectid")     
        
        def setProjectName(self,projectname):
                """
                projectname: A string containing the name of the project associated with
                a repository.
                """
                self.setMetadataAttribute("projectname",projectname)
        
        def getProjectName(self):
                return self.getMetadataAttribute("projectname")
                
        def setURL(self,url):
                """
                url: A string containing the URL that points to the repository where the
                data in this file was mined.
                """
                self.setMetadataAttribute("url",url)
        
        def getURL(self):
                return self.getMetadataAttribute("url")
                
        def getColumnNames(self):
                return self.getMetadataAttribute("names")
        
        def setColumnNames(self,names):
                """
                names: A list of strings containing the (in-order)
                names for each of the columns.
                """
                self.setMetadataAttribute("names",names)
        
        def getColumnDatatypes(self):
                return self.getMetadataAttribute("datatypes")
                
        def setColumnDatatypes(self,datatypes):
                """
                datatypes: A list of strings describing the data
                types for each of the columns.
                """
                return self.setMetadataAttribute("datatypes",datatypes)
                
        def addRecord(self,record):
                """
                record: A list of objects containing the data needed
                to write out a record. Records are guaranteed to be
                written out in the order that they were received.
                """
                self._records.append(record)
                
        def getRawRecords(self):
                """
                Get a list of lists, each containing the data associated
                with the record. This method is provided for testing purposes
                and users should call getRecordsForDicts instead.
                """
                return self._records
                
        def getRecordsAsDicts(self):
                """
                Returns a list of dictionaries, one for each record, that maps
                the names of columns to their respective data in the files.
                """
                columnNames = self.getColumnNames()
                recordDicts = []
                for record in self._records:
                        recordDict = {}
                        for index in range(len(columnNames)):
                                recordDict[columnNames[index]] = record[index]
                        recordDicts.append(recordDict)
                return recordDicts        
                
        def validateMetadata(self):
                hasExecutionID = self.getReposcannerExecutionID() is not None
                hasCreator = self.getCreator() is not None
                hasDateCreated = self.getDateCreated() is not None
                hasProjectID = self.getProjectID() is not None
                hasProjectName = self.getProjectName() is not None
                hasURL = self.getURL() is not None
                hasColumnNames = len(self.getColumnNames()) > 0
                hasColumnDatatypes = len(self.getColumnDatatypes()) > 0
                
                return hasExecutionID and hasCreator and hasDateCreated \
                and hasProjectID and hasProjectName and hasURL \
                and hasColumnNames and hasColumnDatatypes
                
        def readFromFile(self):
                def readMetadataFromFile(text):
                        try:
                                #TODO: This may turn out to be a fragile way of parsing the
                                #metadata line if the metadata value has spaces in it.
                                #m = re.match("#([a-zA-Z]+)\w+(.*?)",text)
                                #return m.group(1),m.group(2)
                                splitResult = text.split()
                                return splitResult[0][1:],splitResult[1]
                        except Exception as e:
                                raise ValueError("Failed to parse metadata in {path}: {text}".format(path=self.getFilePath(),text=text))
                with open(self.getFilePath(), 'r', newline='\n') as f:
                        csvreader = csv.reader(f, delimiter=',', quotechar='|')
                        currentlyReadingMetadata = True
                        for row in csvreader:
                                if currentlyReadingMetadata:
                                        if len(row) > 0 and row[0][0] == '#':
                                                metadataKey,metadataValue = readMetadataFromFile(row[0])
                                                if metadataKey == "names" or metadataKey == "datatypes":
                                                        #TODO: Parse names and datatypes, which are lists delimited
                                                        #by semicolons.
                                                        metadataValue = metadataValue.split(sep=';')
                                                        self.setMetadataAttribute(metadataKey,metadataValue)
                                                else:
                                                        if metadataKey == "datecreated":
                                                                metadataValue = datetime.date.fromisoformat(metadataValue)
                                                        self.setMetadataAttribute(metadataKey,metadataValue)
                                        else:
                                                currentlyReadingMetadata = False
                                else:
                                        self.addRecord(row)
                                        
        
        def writeToFile(self):
                def writeMetadataFieldToFile(csvwriter,key,value):
                        csvwriter.writerow(["#{key} {value}".format(key=key,value=value)])
                with open(self.getFilePath(), 'w', newline='\n') as f:
                        csvwriter = csv.writer(f, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        
                        #Expected Metadata for CSV files.
                        executionid = self.getReposcannerExecutionID()
                        creator = self.getCreator()
                        dateCreated = self.getDateCreated()
                        projectID = self.getProjectID()
                        projectName = self.getProjectName()
                        url = self.getURL()
                        names = ";".join(self.getColumnNames())
                        datatypes = ";".join(self.getColumnDatatypes())
                        
                        writeMetadataFieldToFile(csvwriter,"executionid",executionid)
                        writeMetadataFieldToFile(csvwriter,"creator",creator)
                        writeMetadataFieldToFile(csvwriter,"datecreated",dateCreated)
                        writeMetadataFieldToFile(csvwriter,"projectid",projectID)
                        writeMetadataFieldToFile(csvwriter,"projectname",projectName)
                        writeMetadataFieldToFile(csvwriter,"url",url)
                        writeMetadataFieldToFile(csvwriter,"names",names)
                        writeMetadataFieldToFile(csvwriter,"datatypes",datatypes)
                        
                        for record in self._records:
                                csvwriter.writerow(record)
                                
                        
                
                
                
                
        