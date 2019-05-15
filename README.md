# Tinkle Messenger
A cross platform chat application which features private and group chats.
Built using the Kivy framework.
## Features
* Global chat with anyone on Tinkle
* Groups
* Private chats
* Friends
* Status
* File sharing

# Usage
## Prerequisites
* Python 3 (tested with v3.7.3)
* Kivy (tested with v1.10.1)

## Server
* Have a webserver installed
    * Place the files in [web server](web_server) to the htdocs directory
* Create a directory where you'd like to run the python server from
    * Place the files in [server](server) into the newly created directory
    * Run [initiate_address.py](server/initiate_address.py) and specify the website address (e.g. http://mysite.com/ or http://192.168.178.20/)
##
Short description of what the server .py files do is found [here](server/readme.md).
##
Run
```
server.py
names.py
display_pics.py
```
And that should be it. The .py files in [here](web_server) do not neccessarily need to be run as they are more or less extras.
#
## Client
Run the following commands
```
pip install requests
pip install dataset
``` 
Edit the address url in ```main.py``` to point your own server

Run ```main.py``` to start up the client
#

## Video tutorial on setting up
https://youtu.be/JlSIrbnHPRw

# Pictures
### Find more in [screenshots](screenshots/)
## Sign in screen
![signin](screenshots/client/signin.png?raw=true "Signin screen")
## Home Screen
![main_screen](screenshots/client/main_chat.png?raw=true "Main Screen")
## Main options
![main_options](screenshots/client/main_options.png?raw=true "Main Options")
