# Nuke Config
Here is a collection of Nuke tools increase efficiency and add functionality. This is intended as a powerful but simple off-the-shelf Nuke config. It mostly contains code and tools I've written, but there are also a few of the more exceptional Nukepedia tools included. 

# Background
I've been a Compositor, Compositing TD, Compositing Lead, Compositing Supervisor and VFX Supervisor. I like to figure out how stuff works, and I like to build things. Most of all I like to make my life efficient. Hopefully these tools come in handy and do the same for you.

# About
There is some documentation in the markdown files [in the doc folder](/doc).

Organizationally, the [tools](/tools) folder contains python scripts. Every folder in here is loaded on launch by the menu.py. There are two modules: [nuketools](/tools/python/nuketools), and [nukepedia](/tools/python/nukepedia). Nuketools are tools I have written, and Nukepedia includes a few very useful scripts from other authors (sometimes with a few modifications). [toolsets](/toolsets) includes Nuke toolsets (gizmos as groups). Here, [jedsmith](/toolsets/jedsmith) contains tools I've written, and [nukepedia](/toolsets/nukepedia) includes tools from [Nukededia](http://www.nukepedia.com).

# Installation

### Option 1: Environment Variable
Download this folder and put it somewhere. We'll say it's in your home directory in `~/nuke-config`. We will add this path to our `NUKE_PATH` environment variable, so that Nuke loads the contents of this folder. 

Add a line to your `~/.bash_profile` (or equivalent): 
`export NUKE_PATH=~/nuke-config:${NUKE_PATH}`

Start Nuke from a new shell and you should see new stuff. This should co-exist with whatever you've set up in your own `.nuke` folder.

### Option 2: Overwrite your .nuke
The second option just overwrites your local `~/.nuke` folder. To do this, simply download this repo, and copy the contents into your `~/.nuke` folder.


# Notes

The contents of the [images](/doc/images) is hosted through [git lfs](https://git-lfs.github.com) so they don't bloat the filesize of the history.