import pytest
import subprocess
import os


def test_GraphViz_isAvailableOnCommandLine() -> None:
    """
    This tests whether we can get a version for Dot.
    The version info should look something like this:
    dot - graphviz version 2.47.3 (20210619.1520)
    """
    versionInfoResult = subprocess.run(
        "dot -V",
        shell=True,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    assert(versionInfoResult.returncode == 0)
    assert(versionInfoResult.stdout is not None)
    assert(len(versionInfoResult.stdout) > 0)
    assert("graphviz" in versionInfoResult.stdout)
