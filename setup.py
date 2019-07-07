from setuptools import setup

include = [
    "**/icons/*.png",
    "**/LICENSE",
    "**/models/misc/*",
]

setup(
    name="DirectGuiDesigner",
    author = "Fireclaw the Fox",
    author_email = "info@grimfang-studio.org",
    options = {
        "build_apps": {
            "include_patterns": include,
            "gui_apps": {
                "directguidesigner": "DirectGuiDesigner.py",
            },
            "plugins": [
                "pandagl",
            ],
            "platforms": [
                "manylinux1_x86_64"
                #"macosx_10_6_x86_64",
                #"win_amd64",
            ],
        }
    }
)
