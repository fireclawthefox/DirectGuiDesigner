import sys
import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler


from panda3d.core import (
    loadPrcFileData,
    loadPrcFile,
    Filename,
    ConfigVariableSearchPath,
)

def setupLog(editor_name):
    # check if we have a config file
    home = os.path.expanduser("~")
    basePath = os.path.join(home, f".{editor_name}")
    if not os.path.exists(basePath):
        os.makedirs(basePath)
    logPath = os.path.join(basePath, "logs")
    if not os.path.exists(logPath):
        os.makedirs(logPath)

    # Remove log files older than 30 days
    for f in os.listdir(logPath):
        fParts = f.split(".")
        fDate = datetime.now()
        try:
            fDate = datetime.strptime(fParts[-1], "%Y-%m-%d_%H")
            delta = datetime.now() - fDate
            if delta.days > 30:
                #print(f"remove {os.path.join(logPath, f)}")
                os.remove(os.path.join(logPath, f))
        except Exception:
            # this file does not have a date ending
            pass

    logfile = os.path.join(logPath, f"{editor_name}.log")
    handler = TimedRotatingFileHandler(logfile)
    consoleHandler = StreamHandler()
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[handler])#, consoleHandler])
    prcFileName = os.path.join(basePath, f".{editor_name}.prc")
    if os.path.exists(prcFileName):
        loadPrcFile(Filename.fromOsSpecific(prcFileName))

        # make sure to load our custom paths
        paths_cfg = ConfigVariableSearchPath("custom-model-path", "").getValue()
        for path in paths_cfg.getDirectories():
            line = "model-path {}".format(str(path))
            loadPrcFileData("", line)
    else:
        with open(prcFileName, "w") as prcFile:
            prcFile.write("skip-ask-for-quit #f\n")
            prcFile.write("create-executable-scripts #f\n")
            prcFile.write("show-toolbar #t\n")
