# Ransomware File Rollback Tool (Under Construction 5/21) 
The Ransomware File Rollback Tool is a Python-based command-line tool that is primarily used to stage a Box tenant with simulations for a ransomware attack. The tool allows for the upload of files, editing of their content legitimately, and re-uploading with file contents encrypted. Thanks to version control in Box, the tool can roll back files to a previous untampered version provided a start window for the "malware/ransomware attack" is provided.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Installation
To use the Ransomware File Rollback Tool, follow these steps:

1. Clone the repository:
```git clone https://github.com/Bullkn0x/ransomware-file-rollback.git```

2. Create a virtual environment and install dependencies:

```bash
cd ransomware-file-rollback
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

3. Create a Box developer account and obtain your Box developer token by following the instructions in the [Box developer documentation](https://developer.box.com/docs/getting-started-box-platform).
4. Create a `config.json` file in the root directory with your Box developer token and other relevant information. A sample `config.json` file is provided in the repository.


## Usage



### Command Line Arguments

The tool can be used via command-line arguments to `run.py` to skip the wizard and go straight to the tool execution. To do this, pass the one or many of the following arguments:

- `-c, --count`: The number of files to create.
- `-u, --update`: Flag to update all the files in the test directory.
- `-enc, --encrypt`: Flag to encrypt the specified number of files.
- `-dec, --decrypt`: Flag to decrypt the specified number of files.
- `-env, --environment`: Specifies how/where to execute (`local`|`boxdrive`|`boxapi`)


### Here are some examples:

#### create and edit 10 sample files locally:

- ```python run.py --create 10 --update -env local```

#### Encrypt files in local sample directory:

- ```python run.py --encrypt -env local```

### CLI Wizard

The tool also has a command-line wizard that will guide you through the steps to simulate a ransomware attack. To use the wizard, run:

```python run.py```

![filewizard](https://im2.ezgif.com/tmp/ezgif-2-436315e1af.gif)

This will start the wizard, which will guide walk you through staging your test environment and executing a file rollback.


### Flask App GUI

![webapp](https://i.imgur.com/4Dh2Hru.png)

The tool can be run through a GUI in a Flask app. To start the Flask app, run:
`python run.py --web`


This will start the app on `localhost:5000`. From here, you can interact with the app through a web browser.





## Features
- Bulk Upload files to Box (via Box Drive and API)
- Bulk edit file contents
- Reupload files with file contents encrypted
- Pull Event Stream events with filters
- Roll back files to a previous version



## License
The Ransomware File Rollback Tool is licensed under the [MIT License](https://github.com/Bullkn0x/ransomware-file-rollback/blob/main/LICENSE).
