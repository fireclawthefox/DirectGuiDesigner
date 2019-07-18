#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
from DirectGuiDesignerPathSelect import DirectGuiDesignerPathSelect


import importlib.util



class DirectGuiDesignerLoaderPy:
    def __init__(self, visualEditor, tooltip):
        self.visualEditor = visualEditor
        self.dlgPathSelect = DirectGuiDesignerPathSelect(
            self.Load, "Load Python File", "Load file path", "Load", "~/export.py", tooltip)

    def Load(self, doLoad):
        if doLoad:
            path = self.dlgPathSelect.getPath()
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)

            spec = importlib.util.spec_from_file_location("loadedGUI", path)
            guiModule = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(guiModule)
            guiModule.GUI(self.visualEditor.getCanvas())

        self.dlgPathSelect.destroy()
        del self.dlgPathSelect
