# plasma-irreg-scint-spectra
Code for calculating conjunctions, spectra, and other analysis

## Setup

1. Clone this repository

   `git clone git@github.com:Polar-Cap-Scintillation/plasma-irreg-scint-spectra.git`
   
   Note that you will have to have a [GitHub ssh key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/about-ssh) set up to do this in a way that will let you contribute changes back to the main repository.

3. Enter the repository working directory.

    `cd plasma-irreg-scint-spectra`

4. Install required packages.

    `pip install -r requirements.txt`

5. Install additional custom required packages.

   `pip install git+https://github.com/Polar-Cap-Scintillation/gnssparser`
   
   `pip install git+https://github.com/Polar-Cap-Scintillation/satgroundconj`
   
   `pip install git+https://github.com/ljlamarche/gnssutils`

   These are packages that contain some of the basic functionality for this analysis.  They may need updates or bug fixes.

## Start
Start a jupyter lab server out of this directory.

`jupyter lab`

## Contents
This folder contains two main notebooks:

- `conjunction_list.ipynb`: Generates a list of In Situ/GNSS conjunctions for a particular ground receiver.
- `conjunction_example.ipynb`: Analysis for a single conjuction.

The python scripts `calculate_conjunctions.py` and `find_scint_events.py` are old, but may be useful at some point.


## Pushing Changes
If you've made changes/additions, they should be pushed back to the github repo so we can all use them.  Do this with the following sequence of git commands.

`git add <list files that have changed>`

`git commit -m "<Describe the changes>"`

`git push`

The command

`git status`

is useful for determining which files have been changed.

DO NOT commit or push data files into the repo.

## Retrieving Updates
Use

`git pull`

to retreive the latest updates.