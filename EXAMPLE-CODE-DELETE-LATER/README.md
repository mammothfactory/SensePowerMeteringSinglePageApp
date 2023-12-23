# TimeTracker
Progressive Web App (PWA) running on "TimeTracker-Debian-US-Southeast" Linode server and deployed at http://timetracker.pagekite.me using www.pagekite.net <br>

To delpoy the PWA to the global internet complete the following steps: <br> 
1. Open "TimeTracker-Debian-US-Southeast" server label in the "blazes@mfc.us" Linode account
2. Click "Launch LISH Console" then select the Weblish tab to run the following commands 
apt-get install python3-venv
python3 -m venv .venv
3. Run the "source .venv/bin/active" command to start Virtual Environment
4. Install extrernal libraries using the "pip3 install -r requirements.txt" command
5. Run the "python3 Main.py &" command in start the main NiceGUI application
6. Run the "python3 pagekite.py 8282 timetracker.pagekite.me" to securely reverse proxy share localhost on Linode to internet


Long Term Deploy Strategy: <br>
https://github.com/zauberzeug/nicegui/issues/469


/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/multiprocessing/resource_tracker.py:216: UserWarning: resource_tracker: There appear to be 12 leaked semaphore objects to clean up at shutdown
  warnings.warn('resource_tracker: There appear to be %d '