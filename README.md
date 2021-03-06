# scriptsforanacreon

**This script collection uses anacreonlib 1.0 and is deprecated**

This library contains Python scripts which automate various tasks in [Anacreon 3](https://anacreon.kronosaur.com), which is an online [4X](https://en.wikipedia.org/wiki/4X) game produced by [Kronosaur Productions, LLC.](http://kronosaur.com/)


The policy surrounding automated interaction with the game can be found [here](https://multiverse.kronosaur.com/news.hexm?id=97) under the section "Scripts and Bots."

## Purpose

Many tasks within the game are tedious, such as building spaceports on newly conquered worlds. These scripts help automate such tasks.

## Usage

I run these scripts from PyCharm. PyCharm does funny things to `PYTHONPATH`. As a result, if you are runnning these outside if PyCharm, you may need to manipulate your `PYTHONPATH`

On a *nix system, as long as you are running from the root directory of the project, the `runscript` bash script will take care of `PYTHONPATH` manipulation for you. 


### Usage of runscript

`./runscript <path to file> <arguments>`

It's like running with the `python` command, but you have `./runscript` there instead. 
