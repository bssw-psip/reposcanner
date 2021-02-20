from reposcanner.manager import ReposcannerManager
from reposcanner.provenance import ReposcannerLabNotebook
import argparse, os, logging
import reposcanner.data as data

logging.basicConfig(filename='reposcanner.log',level=logging.DEBUG)

def scannerMain(args):
        """
        The master routine for Reposcanner.
        """
        
        notebook = ReposcannerLabNotebook()
        
        dataEntityFactory = data.DataEntityFactory()
        
        repositoriesDataFile = dataEntityFactory.createYAMLData(args.repositories)
        credentialsDataFile = dataEntityFactory.createYAMLData(args.credentials)
        configDataFile = dataEntityFactory.createYAMLData(args.config)
        
        repositoriesDataFile.readFromFile()
        credentialsDataFile.readFromFile()
        configDataFile.readFromFile()
        
        notebook.onStartup(args)
        
        manager = ReposcannerManager(notebook=notebook,outputDirectory=args.outputDirectory,workspaceDirectory=args.workspaceDirectory,gui=args.gui)
        manager.run(repositoriesDataFile,credentialsDataFile,configDataFile)
        
        notebook.onExit()
        notebook.publishNotebook(args.notebookOutputPath)
        
        
        

if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='The IDEAS-ECP PSIP Team Repository Scanner.')
        parser.add_argument('--repositories', action='store', type=str, help='A list of repositories to collect data on, a YAML file (see example).')
        parser.add_argument('--credentials', action='store', type=str, help='A list of credentials needed to access the repositories, a YAML file (see example).')
        parser.add_argument('--config', action='store', type=str, help='A YAML file specifying what routines and analyses Reposcanner should run (see example).')
        parser.add_argument('--outputDirectory',action='store',type=str,default='./',help='The path where Reposcanner should output files. \
                By default this is done in the directory from which this script is run.')
        parser.add_argument('--notebookOutputPath',action='store',type=str,default="./notebook.log",help='The path where Reposcanner should output a file containing a log that \
                describes this run.')
        parser.add_argument('--workspaceDirectory',action='store',type=str,default='./',help='The path where Reposcanner should make clones of repositories. \
                By default this is done in the directory from which this script is run.')
        parser.add_argument('--gui',action='store_true',help="Enables GUI mode, which provides a dynamically refreshed console view of \
        Reposcanner's progress.")
        args = parser.parse_args()
        scannerMain(args)
        
