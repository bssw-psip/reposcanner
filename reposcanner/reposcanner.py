from reposcanner.manager import ReposcannerRoutineManager
import argparse, os, logging
import yaml

logging.basicConfig(filename='reposcanner.log',level=logging.DEBUG)

def loadYAMLFile(filePath):
        """
        Load in a YAML file containing the repositories the user wants to collect data on.
        
        filePath: The path to the YAML file, a string.
        """
        if not os.path.exists(filePath):
                raise OSError("Reposcanner couldn't find the YAML file ({path})\
                Shutting down as a precaution.".format(path=filePath))
        with open(filePath) as f:
                try:
                        contents = yaml.safe_load(f)
                except yaml.YAMLError as exception:
                        print("While loading a YAML file ({path}), Reposcanner encountered \
                        an exception via PyYAML.".format(path=filePath))
                        raise exception
                if contents == None:
                        raise OSError("PyYAML tried parsing a file ({path}), but that \
                        result was None, which means it failed to read the contents of \
                        the file.".format(path=filePath))
        return contents
                
                

def scannerMain(args):
        """
        The master routine for Reposcanner.
        """
        repositoryDictionary = loadYAMLFile(args.repositories)
        credentialsDictionary = loadYAMLFile(args.credentials)
        
        manager = ReposcannerRoutineManager(outputDirectory=args.outputDirectory,workspaceDirectory=args.workspaceDirectory,gui=args.gui)
        manager.run(repositoryDictionary=repositoryDictionary,credentialsDictionary=credentialsDictionary)
        
        
        

if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='The IDEAS-ECP PSIP Team Repository Scanner.')
        parser.add_argument('--repositories', action='store', type=str, help='A list of repositories to collect data on, a YAML file (see example).')
        parser.add_argument('--credentials', action='store', type=str, help='A list of credentials needed to access the repositories, a YAML file (see example).')
        parser.add_argument('--outputDirectory',action='store',type=str,default='./',help='The path where Reposcanner should output files. \
                By default this is done in the directory from which this script is run.')
        parser.add_argument('--workspaceDirectory',action='store',type=str,default='./',help='The path where Reposcanner should make clones of repositories. \
                By default this is done in the directory from which this script is run.')
        parser.add_argument('--gui',action='store_true',help="Enables GUI mode, which provides a dynamically refreshed console view of \
        Reposcanner's progress.")
        args = parser.parse_args()
        scannerMain(args)
        
