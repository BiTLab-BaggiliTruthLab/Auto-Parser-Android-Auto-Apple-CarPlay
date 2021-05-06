# Carplay-and-Auto-Tool
Welcome to the Android Auto and Apple CarPlay Parser. This tool is part of a research paper conduceted on the digital forensics of Android Auto and Apple Carplay.

To use this tool, please follow these steps below:

## Setup
To setup this tool, it is advised to configure a virtual environment inside the tool directory. To do this, navigate into the tool's main folder and enter the following commands documented below. These commands will setup a virtual environment inside the directory which will allow you to install the dependencies for this tool:

```bash
$ python3 -m venv ./virtualenv
```

To activate or deactivate the environment:
```bash
$ ./virtualenv/Scripts/activate
$ deactivate
```


Once you have setup the virtual environment it is important to install the necessary dependencies for this tool by running the command: 

```bash
$ pip install -r requirements.txt
```


## Command line arguments

Executing the tool is very simple and straight forward. 
The tool is setup to use default wordlists in order to provided a tailored report file documenting what we believe to be the most important data for an investigation. However, if you wish to use your own wordlist there is a option to do so. The following options are available:

```bash
Usage:   Tool.py [options] <inputfile>
Example: Tool.py -a Apple.tar -w wordlist.txt
Options:
         -h, --help
         -a            apple image tar
         -b            android image tar
         -w            wordlist
```

Upon execution of the tool with the necessary options, the tool will ask for a Case Number and name of Examiner to preserve the chain of custody. Additionally, there is a built in feature to hash the TAR files before and after execution of the tool to ensure that the data has not been tampered.

## Report & Artifact Generation
Once the tool is run, a customized report is generated for either Android Auto or Apple CarPlay. Currently it only supports documentation for the information we deemed important to convey. However, our tool extracts and separates the files defined in the wordlists to a folder named after the case file and image source type (ex: 00001-Apple).
