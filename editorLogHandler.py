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

def setupLog(editor_name, log_to_console=False):
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

    log_file = os.path.join(logPath, f"{editor_name}.log")
    handler = TimedRotatingFileHandler(log_file)
    consoleHandler = StreamHandler()
    logHandlers = [handler]
    if log_to_console:
        logHandlers.append(consoleHandler)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=logHandlers)

    config_file = os.path.join(basePath, f".{editor_name}.prc")
    if os.path.exists(config_file):
        loadPrcFile(Filename.fromOsSpecific(config_file))

        # make sure to load our custom paths
        paths_cfg = ConfigVariableSearchPath("custom-model-path", "").getValue()
        for path in paths_cfg.getDirectories():
            line = "model-path {}".format(str(path))
            loadPrcFileData("", line)
    else:
        with open(config_file, "w") as prcFile:
            prcFile.write("skip-ask-for-quit #f\n")
            prcFile.write("create-executable-scripts #f\n")
            prcFile.write("show-toolbar #t\n")

    return log_file, config_file
