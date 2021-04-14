"""Need to store...
Timestamp when the run started.
Timestamp when the run finished.
Unique identifier for the run (to stamp the output data with).
Elapsed time.
The version of Reposcanner used.
Number of tasks processed, number of repositories mined.
What routines failed to complete and for which repositories.
Which routines were run (and the parameters, if any, that they were run with).
Which analyses were run, what data they used, and what results they generated.
What files were created (plus hashes of those files).

The fundamental data structure for provenance is a directed acyclic graph (DAG), 
where the nodes are process invocations and information about data, called process and data nodes respectively.

An abstract workflow may be specified as a pre-determined set of steps. Execute A, then B, then C. 
The focus of a provenance model is to capture information about what actually took place. 
As such, the model does not capture abstract workflow specifications because they are not part of the record of what happened. 
Abstract workflows do though typically contain things such as loop constructs, conditional execution statements and other artifacts. 
These additional artifacts can be quite useful depending on the application scenario; application developers 
may choose to capture and manage these separately, but outside of the scope of the provenance application.
"""
from abc import ABC, abstractmethod
import datetime,json,uuid,sys,subprocess,os
import reposcanner.data as dataEntities

"""
trungdong/prov, a W3C-compliant provenance Data Model 
supporting PROV-O (RDF), PROV-XML, PROV-JSON, and import/export.
"""
import prov.model as prov
from prov.dot import prov_to_dot


class ReposcannerRunInformant:
        """
        This class is responsible for defining and providing key
        information for provenance tracking, including a unique
        identifier for the run of Reposcanner.
        """
        
        #A class variable that uniquely defines the current
        #run of Reposcanner.
        EXECUTIONID = uuid.uuid1().hex
        
        def getReposcannerExecutionID(self):
                """
                Return a unique identifier string associated with the current run of
                Reposcanner.
                This is determined at the time that the ReposcannerRunInformant
                class is first loaded into memory by the interpreter.
                """
                return ReposcannerRunInformant.EXECUTIONID
                
        def getReposcannerVersion(self):
                """
                Return a string indicating what version of Reposcanner was used for this run.
                Since we aren't yet versioning releases of the tool, this is the hash of the
                current revision/commit of Reposcanner.
                """
                try:
                        completedProcess = subprocess.run(["git", "log", "--pretty=format:'%h'", "-n 1"])
                        return completedProcess.stdout
                except Exception as e:
                        return "UNKNOWN"
                
        



class AbstractLabNotebook(ABC):
        """
        Abstract base class for classes that encapsulate provenance-tracking code
        for runs of the Reposcanner tool.
        """
        
        @abstractmethod
        def onStartup(self,args):
                """
                Called when Reposcanner is first initialized.
                
                args: Any command-line arguments passed to the main method of Reposcanner.
                """
                pass
                
        @abstractmethod
        def onExit(self):
                """
                Called when Reposcanner has finished execution.
                """
                pass
        
        @abstractmethod
        def onRoutineCreation(self,routine):
                """
                Called when a RepositoryRoutine object is created during initialization.
                
                routine: The RepositoryRoutine object.
                """
                pass
                
        @abstractmethod
        def onAnalysisCreation(self,analysis):
                """
                Called when an DataAnalysis object is created during initialization.
                
                analysis: The DataAnalysis object.
                """
                pass
        
        @abstractmethod
        def onTaskCreation(self,task):
                """
                Called when a ManagerTask object is created.
                
                task: The ManagerTask object.
                """
                pass
                
        @abstractmethod
        def onTaskStart(self,task,store,agent):
                """
                Called when a ManagerTask object is created.
                
                task: The ManagerTask object.
                store: A DataEntityStore instance provided by the manager responsible for the task.
                agent: The RepositoryRoutine or DataAnalysis object that is expected to handle the task.
                """
                pass
        
        @abstractmethod     
        def onTaskCompletion(self,task,agent):
                """
                Called when a ManagerTask object has been processed and has received a response.
                
                task: The ManagerTask object.
                agent: The RepositoryRoutine or DataAnalysis object that is expected to handle the task.
                """
                pass
        
        @abstractmethod        
        def publishNotebook(self):
                """
                Output the lab notebook's contents to a file.
                
                outputPath: The path to the file where the provenance records will be written.
                """
                pass

class ReposcannerLabNotebook(AbstractLabNotebook):
        """
        This is the default implementation of the lab notebook. We may
        want to create more specialized versions of this notebook in future
        releases of Reposcanner, which is why we have an abstract base
        class.
        """
        
        def __init__(self,notebookOutputDirectory):
                """
                notebookOutputDirectory: The directory where provenance files should be stored when calling
                publishNotebook().
                """
                self._document = prov.ProvDocument()
                self._document.add_namespace('rs', 'reposcanner/')
                
                self._notebookOutputDirectory = notebookOutputDirectory
                if not os.path.isdir(self._notebookOutputDirectory) or not os.path.exists(self._notebookOutputDirectory):
                        raise IOError("The notebook output directory {notebookOutputDirectory} either does not exist or \
                        is not a valid directory.".format(notebookOutputDirectory=self._notebookOutputDirectory))
                if not os.access(self._notebookOutputDirectory, os.W_OK):
                        raise IOError("Reposcanner does not have permissions to write to the notebook output directory \
                        {notebookOutputDirectory}.".format(notebookOutputDirectory=self._notebookOutputDirectory))
        
        
        def getJSONRepresentation(self):
                """
                Returns the underlying Prov document in JSON form for testing purposes.
                """
                serialized = self._document.serialize()
                return json.loads(serialized)
                
        def getProvnRepresentation(self):
                """
                Returns the underlying Prov document in PROV-N form for testing purposes.
                """
                return self._document.get_provn()
        
        def onStartup(self,args):
                """
                Called when Reposcanner is first initialized.
                
                args: Any command-line arguments passed to the main method of Reposcanner.
                """
                
                informant = ReposcannerRunInformant()
                
                
                self._document.agent(identifier="rs:ReposcannerManager",other_attributes=(
                ('rs:executionID', informant.getReposcannerExecutionID()),
                ('rs:reposcannerVersion', informant.getReposcannerVersion())
                ))
                
                repositoryListEntity = self._document.entity('rs:repositories',(
                    (prov.PROV_TYPE, "File"),
                    ('rs:path', args.repositories),
                    ('rs:creator', "user")
                ))
                
                credentialsListEntity = self._document.entity('rs:credentials',(
                    (prov.PROV_TYPE, "File"),
                    ('rs:path', args.credentials),
                    ('rs:creator', "user")
                ))
                
                configListEntity = self._document.entity('rs:config',(
                    (prov.PROV_TYPE, "File"),
                    ('rs:path', args.config),
                    ('rs:creator', "user")
                ))
                
                self._document.wasInformedBy("rs:ReposcannerManager", repositoryListEntity)
                self._document.wasInformedBy("rs:ReposcannerManager", credentialsListEntity)
                self._document.wasInformedBy("rs:ReposcannerManager", configListEntity)
                
        def onExit(self):
                """
                Called when Reposcanner has finished execution.
                """
                pass
        
        def onRoutineCreation(self,routine):
                """
                Called when a RepositoryRoutine object is created during initialization.
                
                routine: The RepositoryRoutine object.
                """
                
                routine = self._document.agent("rs:{clazz}".format(clazz=routine.__class__.__name__))
                self._document.actedOnBehalfOf(routine,"rs:ReposcannerManager")
                
        def onAnalysisCreation(self,analysis):
                """
                Called when an DataAnalysis object is created during initialization.
                
                analysis: The DataAnalysis object.
                """
                analysis = self._document.agent("rs:{clazz}".format(clazz=analysis.__class__.__name__))
                self._document.actedOnBehalfOf(analysis,"rs:ReposcannerManager")
        
        def onTaskCreation(self,task):
                """
                Called when a ManagerTask object is created.
                
                task: The ManagerTask object.
                """
                
                task = self._document.activity("rs:task{taskid}".format(taskid=id(task)),other_attributes=(
                                    ('rs:requestType', task.getRequestClassName()),
                                    ('rs:projectID', task.getProjectID()),
                                    ('rs:projectName', task.getProjectName()),
                                    ('rs:URL', task.getURL())
                        )
                )
                
                self._document.wasGeneratedBy("rs:ReposcannerManager",task)
                
        def onTaskStart(self,task,store,agent):
                """
                Called when a ManagerTask object is created.
                
                task: The ManagerTask object.
                store: A DataEntityStore instance provided by the manager responsible for the task.
                agent: The RepositoryRoutine or DataAnalysis object that is expected to handle the task.
                """
                taskID = "rs:task{taskid}".format(taskid=id(task))
                agentID = "rs:{clazz}".format(clazz=agent.__class__.__name__)
                
                startTime = datetime.datetime.now()
                
                self._document.wasStartedBy(activity=taskID,trigger=agentID,time=startTime)
                
                #If the request is an analysis request, we can probe the request to see which
                #files it intends to grab from the data store.
                request = task.getRequest()
                if request.isAnalysisRequestType():
                        filesToBeUsedInAnalysis = store.getByCriteria(request.getDataCriteria())
                        for entity in filesToBeUsedInAnalysis:
                                entityID = None
                                if isinstance(attachment,dataEntities.ReposcannerDataEntity):
                                        entityID = 'rs:dataentity:{objID}'.format(objID=id(entity)) 
                                else:
                                        entityID = 'rs:dataentity:nonstandard:{objID}'.format(objID=id(entity))
                                self._document.usage(taskID,entityID)
        
        def logAdditionalDataEntity(self,entity):
                """
                Convenience method added to enable us to log reposcanner-data files added
                to the data store at start-up.
                """
                dataEntityID = 'rs:dataentity:{objID}'.format(objID=id(attachment))
                dataEntity = self._document.entity(dataEntityID,(
                    (prov.PROV_TYPE, "File"),
                    ('rs:executionID', attachment.getReposcannerExecutionID()),
                    ('rs:path', attachment.getFilePath()),
                    ('rs:creator', attachment.getCreator()),
                    ('rs:md5hash', str(entity.getMD5Hash())),
                )) 
             
        def onTaskCompletion(self,task,agent):
                """
                Called when a ManagerTask object has been processed and has received a response.
                
                task: The ManagerTask object.
                """
                taskID = "rs:task{taskid}".format(taskid=id(task))
                agentID = "rs:{clazz}".format(clazz=agent.__class__.__name__)
                
                endTime = datetime.datetime.now()
                taskWasSuccessful = task.getResponse().wasSuccessful()
                taskMessage = task.getResponse().getMessage()
                self._document.wasEndedBy(activity=taskID,trigger=agentID,time=endTime,other_attributes=(
                        ("rs:wasSuccessful",taskWasSuccessful),
                        ("rs:message",str(taskMessage))        
                ))
                
                if taskWasSuccessful:
                        attachments = task.getResponse().getAttachments()
                        for attachment in attachments:
                                if isinstance(attachment,dataEntities.ReposcannerDataEntity):
                                        md5Hash = None
                                        if attachment.fileExists():
                                                md5Hash = attachment.getMD5Hash()
                                        dataEntityID = 'rs:dataentity:{objID}'.format(objID=id(attachment))
                                        dataEntity = self._document.entity(dataEntityID,(
                                            (prov.PROV_TYPE, "File"),
                                            ('rs:executionID', attachment.getReposcannerExecutionID()),
                                            ('rs:path', attachment.getFilePath()),
                                            ('rs:creator', attachment.getCreator()),
                                            ('rs:dateCreated', str(attachment.getDateCreated())),
                                            ('rs:md5hash', str(md5Hash)),
                                        ))
                                        
                                        if isinstance(attachment,dataEntities.AnnotatedCSVData):
                                                dataEntity.add_attributes((
                                                        ('rs:projectID', attachment.getProjectID()),
                                                        ('rs:projectName', attachment.getProjectName()),
                                                        ('rs:URL', attachment.getURL()),
                                                ))
                                        self._document.wasGeneratedBy(dataEntityID,taskID)
                                        self._document.wasAttributedTo(dataEntityID,agentID)
                                else:
                                        """
                                        Routines are free to return objects that are not of the type ReposcannerDataEntity,
                                        but the provenance of that data is harder to track.
                                        """
                                        dataEntityID = 'rs:dataentity:nonstandard:{objID}'.format(objID=id(attachment))
                                        dataEntity = self._document.entity(dataEntityID,(
                                            ('rs:dataType',str(attachment.__class__.__name__)),
                                            ))
                                        self._document.wasGeneratedBy(dataEntityID,taskID)
                                        self._document.wasAttributedTo(dataEntityID,agentID)
                
             
        def publishNotebook(self):
                """
                Output the lab notebook's contents to a file.
                
                outputPath: The path to the file where the provenance records will be written.
                """
                informant = ReposcannerRunInformant()
                executionID = informant.getReposcannerExecutionID()
                versionInfo = informant.getReposcannerVersion()
                todayDate = datetime.date.today()
                
                #Output dot files representing provenance log.
                dotRepresentation = prov_to_dot(self._document)
                dotRepresentation.write_png("{outputPath}/run_{executionID}.png".format(outputPath=self._notebookOutputDirectory,executionID=executionID))
                dotRepresentation.write_raw("{outputPath}/run_{executionID}.dot".format(outputPath=self._notebookOutputDirectory,executionID=executionID))
                
                #Output PROV-N representation of provenance log.
                provnRepresentation =  self.getProvnRepresentation()
                with open("{outputPath}/provn_{executionID}.log".format(outputPath=self._notebookOutputDirectory,executionID=executionID),'w') as provnFile:
                        provnFile.write(provnRepresentation)
                
                #Output Markdown template for this run.
                with open("{outputPath}/report_{executionID}.md".format(outputPath=self._notebookOutputDirectory,executionID=executionID),'w') as markdownFile:
                        markdownFile.write("# Reposcanner Lab Notebook Template\n\n")
                        
                        markdownFile.write("## Date of Notebook Entry\n")
                        markdownFile.write("{today}\n\n".format(today=todayDate))
                        
                        markdownFile.write("## Title of Run\n")
                        markdownFile.write("Add descriptive name here.\n\n")
                        
                        markdownFile.write("## Research Question(s)\n")
                        markdownFile.write("Add research questions here.\n\n")
                        
                        markdownFile.write("## Data Mining Tool(s) Used\n")
                        markdownFile.write("1. Reposcanner (version {versionInfo}, execution id {executionID})\n\n".format(versionInfo=versionInfo,executionID=executionID))
                        
                        routinesAndAnalyses = [] #TODO: Collect all the names of the routines/analyses used.
                        
                        markdownFile.write("## Reposcanner\n")
                        markdownFile.write("Date of Run | Reposcanner version | Reposcanner Routines/Analyses Run\n")
                        markdownFile.write("----------------------- | ------------------- | -----------\n")
                        markdownFile.write("{today} | {versionInfo} | {routinesAndAnalyses}\n\n".format(today=todayDate,versionInfo=versionInfo,routinesAndAnalyses=";".join(routinesAndAnalyses)))
                        
                        markdownFile.write("## Database Element(s)\n")
                        markdownFile.write("Name of data file(s) | Data file version (date of commit)\n")
                        markdownFile.write("------------------------ | ------------------------------\n")
                        #TODO: List out all the reposcanner-data data entities.
                        markdownFile.write("\n")
                        
                        
                        markdownFile.write("## Method\n")
                        markdownFile.write("## What was done, how\n\n")
                        
                        markdownFile.write("## Resulting Figures, Tables, Images and Discussion\n")
                        markdownFile.write("Name of image | location\n")
                        markdownFile.write("------------------------ | ------------------------------\n")
                        #TODO: Grab any references to files generated by analyses.
                        markdownFile.write("\n")
                        
                        markdownFile.write("Place description and images here.\n")
                        
                        markdownFile.write("## Conclusions or Discussion\n")
                        markdownFile.write("Interpret results\n\n")
                        
                        markdownFile.write("## Follow Up task list\n")
                        markdownFile.write("- [x] this is a complete item\n")
                        markdownFile.write("- [ ] this is an incomplete item\n\n")
                        
                        markdownFile.write("## References\n")
                        markdownFile.write("1. Reference A\n")
                        markdownFile.write("1. Reference B\n\n")
                
                
                
                
                
                