import pytest
import reposcanner.provenance as provenance

def test_ReposcannerRunInformant_isDirectlyConstructible():
        informant = provenance.ReposcannerRunInformant()

def test_ReposcannerRunInformant_differentInstancesProvideTheSameExecutionID():
        informantA = provenance.ReposcannerRunInformant()
        informantB = provenance.ReposcannerRunInformant()
        
        executionIDA = informantA.getReposcannerExecutionID()
        executionIDB = informantB.getReposcannerExecutionID()
        
        assert(executionIDA == executionIDB)

def test_ReposcannerLabNotebook_isDirectlyConstructible():
        notebook = provenance.ReposcannerLabNotebook()
        
def test_ReposcannerLabNotebook_canStoreArgsOnStartup():
        notebook = provenance.ReposcannerLabNotebook()
        args = type('', (), {})()
        args.repositories = "repositories.yaml"
        args.credentials = "credentials.yaml"
        notebook.onStartup(args)
        jsonDocument = notebook.getJSON()
        print(jsonDocument)
        assert(jsonDocument['entity']['rs:repositories']['rs:path'] == 'repositories.yaml')
        assert(jsonDocument['entity']['rs:credentials']['rs:path'] == 'credentials.yaml')
        
        
        