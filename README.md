# SensePowerMeteringSinglePageApp
Simple WPA to display the cost electrical  power measured by the Sense Flex product 

Progressive Web App (PWA) running on "Sense-Power-Metering" Linode server https://cloud.linode.com/linodes/53323885 (OR MFC Jupiter server) and deployed at http://energy-got.pagekite.me using www.pagekite.net <br>

We are using the Sense Flex hardware found at https://sense.com <br>

3rd party API library used to collect data can be found at https://github.com/scottbonline/sense <br>

To delpoy the PWA to the global internet on Linode complete the following steps: <br> 
1. Open "https://cloud.linode.com/linodes/53323885" server label in the "blazes@mfc.us" Linode account
2. Click "Launch LISH Console" then select the Weblish tab to run the following commands 
apt-get install python3-venv
python3 -m venv .venv
3. Run the "source .venv/bin/active" command to start Virtual Environment
4. Install extrernal libraries using the "pip3 install -r requirements.txt" command
5. Run the "python3 MainApp.py &" command to start the main NiceGUI application
6. Run the "python3 pagekite.py 8282 energy-got.pagekite.me" to securely reverse proxy share localhost on Linode to internet

<br>

To delpoy the PWA to the global internet on Jupiter server complete the following steps: <br> 
1. Run the "ssh jupiter@mgpt.ddns.net" command to connect to the MFC AI GPU Jupiter server in Marianna, Florida
2. Run the "cd Apps/SensePowerMeteringSinglePageApp/" command to navigate to the project code 
3. Run the "source .venv/bin/active" command to start Virtual Environment
4. Install extrernal libraries using the "pip3 install -r requirements.txt" command
5. Run the "python3 MainApp.py &" command to start the main NiceGUI application
6. Run the "python3 pagekite.py 8282 energy-got.pagekite.me" to securely reverse proxy share localhost on Jupiter server to internet
