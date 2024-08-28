# Setup Developer Environment

## Context Description

This page contains instructions on how to get and run deployment-support-tooling-cli on Windows or Linux environment.

## Prerequisites

* Java 1.7 / 1.8 installed.
* maven 3.6.x installed & able to build RPMs
* Access to the [Gerrit - Postgres-lib repo](https://gerrit.ericsson.se/#/admin/projects/OSS/ENM-Parent/SQ-Gate/com.ericsson.oss.itpf.datalayer/postgres-lib)
* root abilities on your development environment

## Follow these steps in order

1. <a href="#chapter1">Install linux requirements for Python development</a>

2. <a href="#chapter2">Python - Download & Make</a>

3. <a href="#chapter3">Python Virtual Environment</a>

4. <a href="#chapter4">Python Requirements</a>

<a name="chapter1"></a>
## Install linux requirements for Python development

**Step 1: Install linux requirements**

Install the build essentials:

<code>sudo apt install build-essential</code>

Check if gcc is working

<code>gcc --version</code>

Other dependencies for developing in Python

<code>sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev</code>

<a name="chapter2"></a>
##  Python - Download & Make

### Python version

Postgres-lib was developed using **Python-3.6.10**

#### Download the linux version of Python

Download [Python 3.6.10 Linux](https://www.python.org/ftp/python/3.6.10/Python-3.6.10.tgz)

*_If the link is not working anymore, try find it elsewhere._*

#### Make Python

**Step 1: Create dev_tools directory**

<code>mkdir ~/dev_tools</code>

**Step 2: Untar download Python-3.6.10**

<code>tar -xzvf Python-3.6.10.tgz -C /home/<<signum>>/dev_tools</code>

**Step 3: Change directory**

<code>cd ~/dev_tools/Python-3.6.10/</code>

**Step 4: Configure Python**

<code>sudo ./configure --enable-optimizations --enable-loadable-sqlite-extensions</code>

**Step 5: Make Python**

<code>sudo make</code>

**Step 6: Make Python - altinstall**

Ensure to use altinstall as this can overwrite the existing Python used by the Linux OS.

<code>sudo make altinstall</code>

<a name="chapter3"></a>
## Python Virtual Environment

**Step 1: Make a new directory for Python virtual environments**

<code>mkdir -p ~/dev_tools/virt_envs</code>

**Step 2: Change directory to virt_envs**

<code>cd ~/dev_tools/virt_envs</code>

**Step 3: Build a new virtual env**

<code>~/dev_tools/Python-3.6.10/python -m venv py36</code>

**Step 4: Change directory to virt_envs**

<code>cd ~/dev_tools/virt_envs</code>

**Step 5: Update Bash Aliases**

By updating the bash aliases we can use shortcuts to activate the virtual Python version.

Update the bash_aliases file to have the following aliases:

<code>alias py36='source /home/signum/dev_tools/virt_envs/py36/bin/activate'</code>

<code>alias pyd='deactivate'</code>

*_Replace "signum" with your home directories name_*

To activate this Python virtual env, type py36 in the command line.

To deactivate any Python virtual environment , type pyd in the command line.

<a name="chapter4"></a>
## Python Pip Requirements

**Step 1: Enable Python 3.6.10 virtual environment**

In the command line type:

<code>py36</code>

**Step 2: Create a requirements file**

Create a python_requirements.txt file on your development environment.

<code>vim ~/dev_tools/python_requirements.txt</code>

**Step 3: Get Python Requirements from Gerrit**

Copy the contents from this file [python_requirements.txt](https://gerrit.ericsson.se/plugins/gitiles/OSS/ENM-Parent/SQ-Gate/com.ericsson.oss.itpf.datalayer/postgres-lib/+/refs/heads/master/python_requirements.txt) into the text file from previous step.

**Step 4: Upgrade Pip**

On a command line enter the following command

<code>pip install --upgrade pip</code>

**Step 5: Pip install the requirements**

On a command line enter the following command pointing to the python_requirements.txt file

<code>while read p; do pip install "$p"; done <python_requirements.txt</code>

*_If you hit any issues during pip install, use Google to fix the issue_*

###Feedback

This SDK is constantly under development.