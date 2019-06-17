from setuptools import setup

exclude = [
    "Screenshots/**",
    "Screenshots"]

setup(
    name='DirectGUIDesigner',
    author = "Fireclaw the Fox",
    author_email = "info@grimfang-studio.org",
    options = {
        'build_apps': {
            'include_patterns': ['**/*'],
            #'exclude_patterns': exclude,
            #'file_handlers':  {'.egg': copyEgg},
            'gui_apps': {
                'directguidesigner': 'DirectGuiDesigner.py',
            },
            'plugins': [
                'pandagl',
            ],
            'platforms': [
                'manylinux1_x86_64'
                #'macosx_10_6_x86_64',
                #'win_amd64',
            ],
        }
    }
)
