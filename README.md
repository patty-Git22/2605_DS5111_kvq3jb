# DS-5111_Software_And_Automation

## Requirements:
	-Log into AWS and set up a VM
	-Make sure to select `Ubuntu Server 26.04`
	-Get SSH key and link to personal Git repo.
* Log into AWS and set up a VM
* Make sure to select `Ubuntu Server 26.04`
* Get SSH key and link to personal Git repo.

## Automating init and setting up virtual environment

### Step 1:Automating the sequence to recreate VM

1. To avoid cloud instance crashes, create a `init.sh` file by typing `nano init.sh` in root directory.
2. Within the `init.sh` file copy and past the following:
	-`sudo apt update` # To bring VM snapshot up to date with package versions
	-`sudo apt install make -y` # so we can use makefiles
	-`sudo apt install python3.14-venv -y` # so we can create python virtual environments
	-`sudo apt install tree` # a usefull tool for listing files in tree form
3. Save and exit. Then type `chmod +x init.sh` to make it executable, followed by `bash init.sh` to run the file.
4. To test to make sure everything ran correctly, you can execute `tree` which will return the name of the init.sh script.

### Step 2: Github Credential Setup

In order for GitHub to recognize who is issuing commits and pushes, we will set up a configuration file in scrpit to allow it to easily be repeatable.

1. Create a `init_git_cred.sh` file using `nano` like before and paste the following into the file:
* To avoid cloud instance crashes, create a `init.sh` file by typing `nano init.sh` in root directory.
* Within the `init.sh` file copy and past the following:
  - `sudo apt update` # To bring VM snapshot up to date with package versions
  - `sudo apt install make -y` # so we can use makefiles
  - `sudo apt install python3.14-venv -y` # so we can create python virtual environments
  - `sudo apt install tree` # a usefull tool for listing files in tree form
* Save and exit. Then type `chmod +x init.sh` to make it executable, followed by `bash init.sh` to run the file.
* To test to make sure everything ran correctly, you can execute `tree` which will return the name of the init.sh sc>

### Step 2: Github Credential Setup

In order for GitHub to recognize who is issuing commits and pushes, we will set up a configuration file in scrpit to >

* Create a `init_git_cred.sh` file using `nano` like before and paste the following into the file:

```bash
!#/usr/bin/bash

USER=<your github email>
NAME=<your github user name>

git config --global --list

git config --global user.email ${USER} 
git config --global user.name  ${NAME} 

git config --global --list
```
2. Replace "<your github email" with the email associated with your github account. Remove ""<>"" as it is not needed.
3. Repeat that step by inserting your github account name below in the `NAME = ` line.
4. Exit and save. Then run the scrpit using the same process as before:
	*make it executable: `chmod +x init_git_creds.sh`
	*run it: `bash init_git_creds.sh`

* Replace "<your github email" with the email associated with your github account. Remove ""<>"" as it is not needed.
* Repeat that step by inserting your github account name below in the `NAME = ` line.
* Exit and save. Then run the scrpit using the same process as before:
  - make it executable: `chmod +x init_git_creds.sh`
  - run it: `bash init_git_creds.sh`


### Step 3: Clone Repo to the machine
In order to save our work to our github repo, we must first clone our repository.
We will clone our repo using `git clone <git@github.com:your_repo_name> which is found by hitting the code button followed by the SSH option on your repo's main page.
Once you have cloned your repo, move into it using `cd <path name>` and following the following steps:
	1. Create a new directory called scripts using `mkdir scripts`.
	2. Move into the new directory `scripts` using `cd scripts`
	3. Move your two init files into it using:
		- `mv ~/init.sh .`
		- `mv ~/init_git_creds.sh .`
	4. Now we are ready to add and commit the files using:
		- `git add .` (you could add each one individually, as in `git add init.sh`.  The command here will add everything in the current directory.
		- `git commit -m "saving our two init files"`
 		- `git push`
	5. Go to your repo page and confirm all files were pushed successfully.

### Step 4: Creating a virtual environment for python and utilizing a makefile for repeatability

Our last task is to acutally make the virtual environment we will be using to intall python. We will also be creating a `makefile` to allows us to easily automate this process.

1. Navigate back to your root directory and create a file called `makefile` and paste the following inside:
```
default:
	@cat makefile

env:
	python3 -m venv; . env/bin/activate; pip install --upgrade pip

update:  env
	
	. env/bin/activate; pip install -r requirements.txt
```


We will clone our repo using `git clone <git@github.com:your_repo_name>` which is found by hitting the code button followed by the SSH option on your repo's main page.
* Create a new directory called scripts using `mkdir scripts`.
* Move into the new directory `scripts` using `cd scripts`
* Move your two init files into it using:
  - `mv ~/init.sh .`
  - `mv ~/init_git_creds.sh .`
* Now we are ready to add and commit the files using:
  - `git add .` (you could add each one individually, as in `git add init.sh`.  The command here will a>
  - `git commit -m "saving our two init files"`
  - `git push`
* Go to your repo page and confirm all files were pushed successfully.

### Step 4: Creating a virtual environment for python and utilizing a makefile for repeatability

Our last task is to acutally make the virtual environment we will be using to intall python. We will also be creating>

* Navigate back to your root directory and create a file called `makefile` and paste the following inside:

```
default:
        @cat makefile

env:
        python3 -m venv env; . env/bin/activate; pip install --upgrade pip

update:  env
        . env/bin/activate; pip install -r requirements.txt
```

* There is no need to make this file executable as it will run when we use the `make` command.
* To test to make sure it is working properly, type `make` and you should see the contents of the file echo to the console.
* Next, we need to make the requirements file that will house the packages we need. To do so, create a file called `requirements.txt` and past the following inside:
 
```
pandas
numpy
```

Now we have everything we need and we can run `make update` to generate our virtual environment. To verify everything is working correctly, we can use `. env/bin/activate`  to activate the enviroment and see (env) to the left of the prompt. We can also confirm everything is working correctly by using `pip list` to return the installed packages, i.e numpy and pandas in this case. Lastly, make sure to push everything to your github repo using the same add/commit/push commands as before.
