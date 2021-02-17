import reposcanner.manager as management

#def test_ManagerRoutineTask_isDirectlyConstructible():
        
#        projectID="PROJID",projectName="SciKit",url="https://github.com/scikit/scikit/",request


def test_ReposcannerManager_isDirectlyConstructible():
        args = type('', (), {})()
        args.outputDirectory = "./"
        args.workspaceDirectory = "./"
        args.gui = True
        manager = management.ReposcannerManager(notebook=None,outputDirectory=args.outputDirectory,workspaceDirectory=args.workspaceDirectory,gui=args.gui)
        
def test_ReposcannerManager_GUIModeIsDisabledByDefault():
        manager = management.ReposcannerManager(notebook=None,outputDirectory=None,workspaceDirectory=None)
        assert(not manager.isGUIModeEnabled())
        
def test_ReposcannerManager_GUIModeCanBeEnabledAtConstructionTime():
        manager = management.ReposcannerManager(notebook=None,outputDirectory=None,workspaceDirectory=None,gui=True)
        assert(manager.isGUIModeEnabled())