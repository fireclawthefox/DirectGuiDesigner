import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DirectGuiDesigner",
    version="22.04.1",
    author="Fireclaw",
    author_email="fireclawthefox@gmail.com",
    description="An editor for the Panda3D engines DirectGUI UI framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fireclawthefox/DirectGuiDesigner",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Artistic Software",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Editors",
    ],
    install_requires=[
        'panda3d',
        'DirectFolderBrowser',
        'DirectGuiExtension'
    ],
    python_requires='>=3.6',
)
