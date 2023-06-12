from reposcanner.manager import ReposcannerManager
import reposcanner.provenance as provenance
import argparse
import os
import logging
import yaml
from pathlib import Path
import reposcanner.data as data

logging.basicConfig(filename='reposcanner.log', level=logging.DEBUG)


# TODO: Update this to be more generic (e.g. allow for reloading of data generated on) previous runs.
# If the file doesn't have readable metadata associated with it, we can just say the creator is
# "external" or unlisted.
def loadReposcannerData(
        reposcannerDataDirectory: str,
        notebook: provenance.ReposcannerLabNotebook,
        manager: ReposcannerManager,
) -> None:
    """
    Read in additional data files held by bssw-psip/reposcanner-data
    and add them to the manager's data store.
    """
    def setupDataEntity(path: str) -> data.ReposcannerDataEntity:
        informant = provenance.ReposcannerRunInformant()
        dataEntityFactory = data.DataEntityFactory()
        dataEntity = dataEntityFactory.createAnnotatedCSVData(path)
        dataEntity.readFromFile()
        dataEntity.setCreator("external")
        dataEntity.setReposcannerExecutionID(informant.getReposcannerExecutionID())
        return dataEntity

    if not os.path.isdir(reposcannerDataDirectory) or not os.path.exists(
            reposcannerDataDirectory):
        raise IOError(
            "The reposcanner-data directory {datadir} either does not exist or \
                is not a valid directory.".format(
                datadir=reposcannerDataDirectory))

    filesToSearchFor = [
        "authors.csv",
        "confluence.csv",
        "folks.csv",
        "folks2.csv",
        "github_login.csv",
        "institutes.csv",
        "members.csv",
        "products.csv",
        "projects.csv",
        "repolist.csv"]

    for fileName in filesToSearchFor:
        filePath = "{datadir}/{name}".format(
            datadir=reposcannerDataDirectory, name=fileName)
        if os.path.exists(filePath):
            dataEntity = setupDataEntity(filePath)
            manager.addDataEntityToStore(dataEntity)
            notebook.logAdditionalDataEntity(dataEntity)


def scannerMain(args: argparse.Namespace) -> None:
    """
    The master routine for Reposcanner.
    """

    Path(args.notebookOutputPath).mkdir(parents=True, exist_ok=True)
    Path(args.outputDirectory).mkdir(parents=True, exist_ok=True)
    notebook = provenance.ReposcannerLabNotebook(args.notebookOutputPath)

    dataEntityFactory = data.DataEntityFactory()

    repositoriesDataFile = dataEntityFactory.createYAMLData(args.repositories)
    credentialsDataFile = dataEntityFactory.createYAMLData(args.credentials)
    configDataFile = dataEntityFactory.createYAMLData(args.config)

    repositoriesDataFile.readFromFile()
    credentialsDataFile.readFromFile()
    configDataFile.readFromFile()

    notebook.onStartup(args)

    manager = ReposcannerManager(
        notebook=notebook,
        outputDirectory=args.outputDirectory,
        workspaceDirectory=args.workspaceDirectory,
        gui=args.gui)

    if args.reposcannerDataDirectory is not None:
        loadReposcannerData(args.reposcannerDataDirectory, notebook, manager)

    manager.run(repositoriesDataFile, credentialsDataFile, configDataFile)

    notebook.onExit()
    notebook.publishNotebook()


argumentList = """
repositories:
    default: inputs/repositories.yml
    help: A list of repositories to collect data on, a YAML file (see example).
credentials:
    default: inputs/credentials.yml
    help: A list of credentials needed to access the repositories, a YAML file (see example).
config:
    default: inputs/config.yml
    help: A YAML file specifying what routines and analyses Reposcanner should run (see example).
outputDirectory:
    default: outputs
    help: |
        The path where Reposcanner should output files.
        By default this is done in the directory from which this script is run.
notebookOutputPath:
    default: notebook
    help: |
        The path where Reposcanner should output files containing
        the logs describing this run.
workspaceDirectory:
    default: "./"
    help: |
        The path where Reposcanner should make clones of repositories.
        By default this is done in the directory from which this script is run.
reposcannerDataDirectory:
    default: null
    help: |
        (Optional) the path where bssw-psip/reposcanner-data is held. At startup,
        Reposcanner will try to pull in additional data files from this directory.
gui:
    type: bool
    help: Enables GUI mode, which provides a dynamically refreshed console view of Reposcanner's progress.
"""


def run() -> None:
    """Calls :func:`scannerMain` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    parser = argparse.ArgumentParser(
        description='The IDEAS-ECP PSIP Team Repository Scanner.')
    for arg, props in yaml.safe_load(argumentList).items():
        # The properties of each argument are passed as keyword
        # arguments to parser.add_argument.
        #
        # This code sets the default action to "store"
        # and the default type to "string".
        # **Unless** "type" is set to "bool", in which
        # case the default action is "store_true".
        try:
            if props["type"] == "bool":
                del props["type"]
                if "action" not in props:
                    props["action"] = "store_true"
        except KeyError:  # default to string type
            props["type"] = str
        if "action" not in props:
            props["action"] = "store"
        parser.add_argument(f"--{arg}", **props)

    args = parser.parse_args()
    scannerMain(args)


if __name__ == "__main__":
    run()
