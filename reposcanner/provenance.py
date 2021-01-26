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
import datetime

def AbstractLabNotebook(ABC):
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
        def onTaskCompletion(self,task):
                """
                Called when a ManagerTask object has been processed and has received a response.
                
                task: The ManagerTask object.
                """
                pass
        
        @abstractmethod        
        def publishNotebook(self,outputPath):
                """
                Output the lab notebook's contents to a file.
                
                outputPath: The path to the file where the provenance records will be written.
                """
                pass

def ReposcannerLabNotebook(AbstractLabNotebook):
        """
        This is the default implementation of the lab notebook. We may
        want to create more specialized versions of this notebook in future
        releases of Reposcanner, which is why we have an abstract base
        class.
        """
        
        def __init__(self):
                pass

        def onStartup(self,args):
                """
                Called when Reposcanner is first initialized.
                
                args: Any command-line arguments passed to the main method of Reposcanner.
                """
                pass
                
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
                pass
                
        def onAnalysisCreation(self,analysis):
                """
                Called when an DataAnalysis object is created during initialization.
                
                analysis: The DataAnalysis object.
                """
                pass
        
        def onTaskCreation(self,task):
                """
                Called when a ManagerTask object is created.
                
                task: The ManagerTask object.
                """
                pass
             
        def onTaskCompletion(self,task):
                """
                Called when a ManagerTask object has been processed and has received a response.
                
                task: The ManagerTask object.
                """
                pass
             
        def publishNotebook(self,outputPath):
                """
                Output the lab notebook's contents to a file.
                
                outputPath: The path to the file where the provenance records will be written.
                """
                pass


"""
class ProvenanceDocument:
        pass
        
        
class ProvenanceRecord(ABC):
        pass
        
class ProvenanceNode(ProvenanceRecord):
        pass
        
class EntityNode(ProvenanceNode):
        pass
        
class ProcessNode(ProvenanceNode):
        pass
        
class AgentNode(ProvenanceNode):
        pass
        
class ProvenanceRelation(ProvenanceRecord):
        pass
        
        
class UsedRelation(ProvenanceRelation):
"""      
        
        
        

class ProvenanceGraphNode(ABC):
        """
        From MITRE's Provenance Capture and Use: A Practical Guide: "The fundamental 
        data structure for provenance is a directed acyclic graph (DAG), where the nodes are 
        process invocations and information about data, called process and data nodes 
        respectively."
        
        This is the abstract base class for Reposcanner's provenance data graph.
        """
        
        def __init__(self,parent=None):
                self._parent = parent
                self._children = []
        
        def isRootNode(self):
                return self._parent == None        
        
        def setParent(self,parent):
                self._parent = parent
                
        def getParent(self):
                return self._parent 
        
        def hasChild(self,child):
                return child in self._children
        
        def addChild(self,child):
                if self.hasChild(child):
                        raise ValueError("Cannot add node as a child because it\
                        already is a child of the given node.")
                self._children.append(child)
                child.setParent(self)
                
        def getChildren(self):
                return self._children
        
        @abstractmethod
        def acceptVisitor(self, visitor):
                """
                Used by ProvenanceGraphVisitors to implement a visitor pattern.
                """
                pass
                

class InvocationNode(ProvenanceGraphNode):
        pass   
                
class DataNode(ProvenanceGraphNode):
        """
        A data node represents data stored in files that is generated and/or consumed
        by Reposcanner's routines and analyses.
        """
        def __init__(self):
                super().__init__()
                
                
                
                