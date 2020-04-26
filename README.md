# PyCraftServerManager

A Python wrapper for Minecraft Servers. Control your Minecraft Server through this Python Package with the normal features + more

# Features

* Start and Stop Server

* Interact with console through Python

* Configure launch options, whitelist, and server properties through Python

* Restart server

* Configure server to launch an Java or Game option. See [`launch_example.properties`](launch_example.properties) for an example.

* Backup Server Files as ZIP or TAR

* Delete User Cache

# Intended Feature List

* Schedule commands are regular intervals

* Configure launch options, whitelist, and server properties through command line

# Required

* Python 3.8 with Pip

* Installation of a Minecraft Server

# Quick Start Installation

1. Clone this repository

1. Run `pip install -r requirements.txt`

1. Modify `run.py` or create your own server starting script.

1. Perform `py run.py` or the equivalent for `run.py` or your script.

1. Run `start` and your server should start up.

# Commands

|    Command Name   |                                                                                                                 Description                                                                                                                | Arguments (blank if none) |
|:-----------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------:|
|  start            |  Starts the Minecraft Server.                                                                                                                                                                                                              |                           |
| stop              |  Stop the Minecraft Server.                                                                                                                                                                                                                |                           |
| restart           | Stops then starts the Minecraft server. If Minecraft server isn't running it will not attempt to start it.                                                                                                                                 |                           |
| backup            | Backs up Minecraft server folder to the folder backups in Project directory. Pass in argument "zip" for server folder to be stored in compressed ZIP folder. Pass in argument "tar" for server folder to be stored in compressed TAR file. | ["tar", "zip"]            |
| exit              |  Quits the Python program. Stops Minecraft server if it is still running.                                                                                                                                                                  |                           |
| delete_user_cache | Deletes `usercache.json` in Minecraft server folder.                                                                                                                                                                                       |                           |

# How-to-Use

In order to use the PyCraftServerManager you can refer to [`run.py`](run.py) or [`example.py`](example.py) on how to use.
