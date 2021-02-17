import reposcanner.manager as management

def test_ReposcannerManager_isDirectlyConstructible():
        args = type('', (), {})()
        args.outputDirectory = "./"
        args.workspaceDirectory = "./"
        args.gui = True
        manager = management.ReposcannerManager(notebook=None,outputDirectory=args.outputDirectory,workspaceDirectory=args.workspaceDirectory,gui=args.gui)