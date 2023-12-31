#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__contact__    = "blazes@mfc.us"
__copyright__  = "Copyright 2024"
__license__    = "MIT License"
__status__     = "Development
__deprecated__ = False
__version__    = "0.1.0"
__doc__        = "Simple script to start NiceGUI PWA frontend and tunneling localhost to the internet"
"""

## Standard Python libraries
import subprocess               # Enable terminal commands to to programmatically run https://docs.python.org/3/library/subprocess.html
from time import sleep          # Import ONLY sleep to save harddrive space https://realpython.com/python-sleep/
import sys                      # Determine which OS this code is running on https://docs.python.org/3/library/sys.html

## Internally developed modules
import GlobalConstants as GC


if __name__ == "__main__":
    try:
        print("Running script to deploy NiceGUI PWA at http://energy-got.pagekite.me")
        command = ['python3', 'MainApp.py', '&']      # & makes command in the background. The shell will NOT wait for command to finish
        startPWA = subprocess.Popen(command).pid
        print(f'Starting PWA PID = {startPWA} and then pausing 10 seconds before tunneling localhost to the internet')

        sleep(10)  # Pause to give the 'python3 MainApp.py &' command time to fully launch the NiceGUI frontend and start stdout logging

        # See https://pagekite.net/support/quickstart/
        command = ['python3', 'pagekite.py', '8282', 'energy-got.pagekite.me']
        tunnelLocalHost = subprocess.Popen(command).pid
        print(f'Tunnelling Local Host PID = {tunnelLocalHost}, you shoudl see PWA at http://energy-got.pagekite.me')

    except KeyboardInterrupt:
        command = []
        if sys.platform.startswith('darwin'):
            # For local MacOS dev
            #command = ['kill', '-9', str(startPWA)]
            command = ['pkill', '-f', '/opt/homebrew/Cellar/python@3.11/3.11.6/Frameworks/Python.framework/Versions/3.11/Resources/Python.app']
        elif sys.platform.startswith('linux'):
            # For Linode server running Debian and Jupiter server running Ubuntu
            command = ['pkill', 'python']
        elif sys.platform.startswith('win'):
            # For Windows dev I have no idea :) PowerShell or WSL2 I leave this work to you Vlad
            print("WARNING: Deploying MainApp.py code on a server running Windows OS is NOT fully supported")
            #command = ['pkill', '-f', 'TODO']
        else:
            print("ERROR: Running on an unknown operating system")
            quit()

        subprocess.Popen(command)
        sleep(10)                               # Pause to give the 'kill -9' command time to close running process
