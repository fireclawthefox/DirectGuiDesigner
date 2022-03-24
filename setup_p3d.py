import sys
from setuptools import setup

include = [
    "**/fonts/*",
    "**/icons/*.png",
    "**/LICENSE",
    "**/models/**",
]

linux64 = "manylinux1_x86_64"
if sys.version_info >= (3, 10):
    linux64 = "manylinux2010_x86_64"
mac64 = "macosx_10_6_x86_64"
win64 = "win_amd64"

setup(
    name="DirectGuiDesigner",
    author = "Fireclaw the Fox",
    author_email = "info@grimfang-studio.org",
    options = {
        "build_apps": {
            "include_patterns": include,
            "gui_apps": {
                "directguidesigner": "main.py",
            },
            "plugins": [
                "pandagl",
            ],
            "platforms": [
                linux64,
                #mac64,
                win64,
            ],

            # make sure to contain the icon directory of the browser
            "package_data_dirs": {
                "DirectFolderBrowser": [
                    ("DirectFolderBrowser/icons*", "", {}),
                ],
            },
        }
    }
)
