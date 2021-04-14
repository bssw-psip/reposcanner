from reposcanner.manager import ReposcannerManager
import reposcanner.provenance as provenance
import argparse, os, logging
import reposcanner.data as data

logging.basicConfig(filename='reposcanner.log',level=logging.DEBUG)


#TODO: Update this to be more generic (e.g. allow for reloading of data generated on) previous runs.
#If the file doesn't have readable metadata associated with it, we can just say the creator is
#"external" or unlisted.
def loadReposcannerData(reposcannerDataDirectory,notebook,manager):
        """
        Read in additional data files held by bssw-psip/reposcanner-data
        and add them to the manager's data store.
        """
        def setupDataEntity(path):
                informant = provenance.ReposcannerRunInformant()
                dataEntityFactory = data.DataEntityFactory()
                dataEntity = dataEntityFactory.createAnnotatedCSVData(path)
                dataEntity.readFromFile()
                dataEntity.setCreator("external")
                dataEntity.setReposcannerExecutionID(informant.getReposcannerExecutionID())
                return dataEntity                
        
        if not os.path.isdir(reposcannerDataDirectory) or not os.path.exists(reposcannerDataDirectory):
                raise IOError("The reposcanner-data directory {datadir} either does not exist or \
                is not a valid directory.".format(datadir=reposcannerDataDirectory))
        
        filesToSearchFor = ["authors.csv","confluence.csv","folks.csv","folks2.csv",
                           "github_login.csv","institutes.csv","members.csv","products.csv",
                           "projects.csv","repolist.csv"]
        
        for fileName in filesToSearchFor:
                filePath = "{datadir}/{name}".format(datadir=reposcannerDataDirectory,name=fileName)
                if os.path.exists(filePath):
                        dataEntity = setupDataEntity(path)
                        manager.addDataEntityToStore(dataEntity)
                        notebook.logAdditionalDataEntity(dataEntity)
        


def scannerMain(args):
        """
        The master routine for Reposcanner.
        """
        
        notebook = provenance.ReposcannerLabNotebook(args.notebookOutputPath)
        
        dataEntityFactory = data.DataEntityFactory()
        
        repositoriesDataFile = dataEntityFactory.createYAMLData(args.repositories)
        credentialsDataFile = dataEntityFactory.createYAMLData(args.credentials)
        configDataFile = dataEntityFactory.createYAMLData(args.config)
        
        repositoriesDataFile.readFromFile()
        credentialsDataFile.readFromFile()
        configDataFile.readFromFile()
        
        notebook.onStartup(args)
        
        manager = ReposcannerManager(notebook=notebook,outputDirectory=args.outputDirectory,workspaceDirectory=args.workspaceDirectory,gui=args.gui)
        
        if args.reposcannerDataDirectory is not None:
                loadReposcannerData(args.reposcannerDataDirectory,notebook,manager)
        
        manager.run(repositoriesDataFile,credentialsDataFile,configDataFile)
        
        notebook.onExit()
        notebook.publishNotebook()
        
        
        

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
        parser.add_argument('--reposcannerDataDirectory',action='store',type=str,default=None,help='(Optional) the path where bssw-psip/reposcanner-data is held. At startup, \
        Reposcanner will try to pull in additional data files from this directory.')
        parser.add_argument('--gui',action='store_true',help="Enables GUI mode, which provides a dynamically refreshed console view of \
        Reposcanner's progress.")
        args = parser.parse_args()
        scannerMain(args)
        
