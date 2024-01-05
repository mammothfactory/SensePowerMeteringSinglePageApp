#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__contact__    = "blazes@mfc.us"
__copyright__  = "Copyright 2023"
__license__    = "MIT License"
__status__     = "Development"
__deprecated__ = False
__version__    = "0.0.1"
__doc__        = "Simple PWA to display the cost of the electrical power measured by the Sense Flex product"
"""

# Disable PyLint linting messages that seem unuseful
# https://pypi.org/project/pylint/
# pylint: disable=invalid-name
# pylint: disable=global-statement

## Standard Python libraries
import sys                                              # Determine which OS this code is running on https://docs.python.org/3/library/sys.html
from datetime import datetime, time, timedelta      	# Manipulate calendar dates & time objects https://docs.python.org/3/library/datetime.html

## 3rd party libraries
# A modern, fast (high-performance), web framework for building APIs with Python 3.8+
# https://fastapi.tiangolo.com
from fastapi import FastAPI                             # Used to connect to UI to the unoffical Sense API https://github.com/scottbonline/sense

# Browser based GUI framework to build and display a user interface on mobile, PC, and Mac
# https://nicegui.io/
from nicegui import app, ui                             # Define highest level app and UI elements
from nicegui.events import ValueChangeEventArguments    # Catch button, radio button, and other user actions

# Unofficial API for the Sense Energy Monitor
# https://github.com/scottbonline/sense
from sense_energy import Senseable                      # Used to connect to the Sense hardware in factory https://sense.com/sense-home-energy-monitor/                      

# Load environment variables for usernames, passwords, & API keys
# https://pypi.org/project/python-dotenv/
from dotenv import dotenv_values                        # Used to login into Sense API

## Internally developed modules
import GlobalConstants as GC                            # Useful global constants used across multiple files
from Database import Database                           # Store non-Personally Identifiable Information in local (to server) SQlite database
import UserInterface                                    # Update the bar graph UI

## Global Variables
api = FastAPI()                             # Method for connection to Sense API https://github.com/scottbonline/sense
sense = Senseable()                         # Object to authenticate and collect realtime trends
instantPower = 0                            # Instant power (in Watts) being measured by the Sense device
dailyEnergyUsage = 0                        # Total energy (in kWh) measured by the Sense device so far (12:01 am to function call time)
currentGuiState = 0                         # State Machine number for the current GUI layout
dateSelected = None                         # Date selcted with left mouse click from the ui.date() calendar element
totalEnergy = 0                             # Units are kWh
selectedView = GC.RADIO_BUTTON_VALUES[0]    # State of radio buttons which defines how energy graph is displayed
canUpdateweeklyReportTable = True           # TODO


"""TODO Connect to https://github.com/scottbonline/sense
@app.get('/')
def root():
    return totalEnergy
"""

"""TODO If Dollar General needs .csv output instead of just website GUI they could screenshot for their bosses (replace ''' if uncommented)
def generate_report(db: Database):
    ''' Generate EXCEL document every monday at 3 am
        Work week starts Sunday at 12:01 am and repeats every 7 days
        Work week ends Saturday at 11:59 pm and repeats every 7 days
        Assumes 12 hour work day at 11 pm if an employee only clocks IN but forgets to clock out
        Back calculates 12 hour work day using the time an employee clocks OUT if no clocking IN exists

    Arg(s):
        db (sqlite): *.db database file
    '''
    
    currentDateObj = db.get_date_time()
    dayOfWeek = currentDateObj.weekday()
    currentTime = currentDateObj.time()

    if dayOfWeek == GC.MONDAY and (ELEVEN_PM < currentTime and currentTime < THREE_AM):
        canUpdateweeklyReportTable = True
        db.export_table_to_csv(["WeeklyReportTable", "CheckInTable", "CheckOutTable"])
"""

def search_button_click(db: Database, selectedView: GC):
    """ Toogle the visibility of GUI elements and draw a SVG bar grpah to create the graph page
    
    Arg(s):
        db (Database): SQlite database file containing all the logged (every GC.SENSE_UPDATE_TIME mintues) energy consumption datapoints
        selectedView (GlobalConstants): A value in the GC.RADIO_BUTTON_VALUES list used to determine which graph view to display
    """
    logo.visible = False
    calendarElement.visible = False
    graph.visible = True
    radioButtons.visible = True
    searchButton.visible = False
    closeGraphButton.visible = True
    graph.set_content(UserInterface.build_svg_graph(db, dateSelected, selectedView))


def close_graph_button_click():
    """ Toogle the visibility of GUI elements to create the home page
    """
    calendarElement.visible = True
    logo.visible = True
    graph.visible = False
    radioButtons.visible = False
    closeGraphButton.visible = False
    searchButton.visible = True


def get_radio_button_state(e: str):
    """ Determine which of the two radio buttons where selected and redraw the bar graph in a WEEKLY or MONTHLY view

    Arg(s):
        e (String): e.value variable created via the ValueChangeEventArguments Class
    """
    global selectedView
    selectedView = e
    graph.set_content(UserInterface.build_svg_graph(db, dateSelected, selectedView))


def get_date_selected(e: str):
    """ Store date clicked on the calendar element by the user into a global variable
    
    Arg(s):
        e (String): e.value variable created via the ValueChangeEventArguments Class
    
    """
    global dateSelected
    dateSelected = e
    if (GC.DEBUG_STATEMENTS_ON): print(f"DateSelected variable was updated: {dateSelected}")


""" TODO Remove if adding SQlite database and FastAPI code doesn't require a State Machine
def check_ui_state_machine():
    ''' Simple state machine to describe the GUI
        State 0 means TODO
        State 1 means TODO
        State 2 means TODO
    '''
    global currentGuiState

    if calendarElement.visible == True and searchButton.visible == True:
        newState = 0
    elif calendarElement.visible == False and searchButton.visible == False:
        newState = 1
    else:
        newState = 2

    currentGuiState = newState
"""


def sense_updating(db: Database, mode: str):
    global instantPower
    global dailyEnergyUsage
    
    sense.update_realtime()
    sense.update_trend_data()
    instantPower = sense.active_power
    dailyEnergyUsage = sense.daily_usage
    
    if GC.DEBUG_STATEMENTS_ON: 
        print (f"{mode} Active: {instantPower} W")
        print (f"{mode} Daily:  {dailyEnergyUsage} kWh")
        print ("Active Devices:",", ".join(sense.active_devices))
        
    current_date = datetime.now()
    year, month, day = current_date.year, current_date.month, current_date.day
    currentDate = str(year) + '-' + str(month) + '-' + str(day)    
    db.insert_daily_energy_table(dailyEnergyUsage, GC.FACTORY_ENERGY_COST, currentDate)    #TODO call SQlite UPDATE if currentDate already exists


if __name__ in {"__main__", "__mp_main__"}:
    # Force application to run in light mode since calendar color is bad in dark mode
    darkMode = ui.dark_mode()
    darkMode.disable()

    ui.colors(primary=GC.DOLLAR_STORE_LOGO_BLUE)

    # Create directory and URI for local storage of images
    if sys.platform.startswith('darwin'):
        app.add_static_files('/static/images', GC.MAC_CODE_DIRECTORY +'/static/images')
        app.add_static_files('/static/videos', GC.MAC_CODE_DIRECTORY + '/static/videos')
    elif sys.platform.startswith('linux'):
        app.add_static_files('/static/images', '/home/jupiter/Apps' + GC.LINUX_CODE_DIRECTORY + '/static/images')
        app.add_static_files('/static/videos', '/home/jupiter/Apps' + GC.LINUX_CODE_DIRECTORY + '/static/videos')
    elif sys.platform.startswith('win'):
        print("WARNING: Running Main.py server code on Windows OS is NOT fully supported")
        app.add_static_files('/static/images', GC.WINDOWS_CODE_DIRECTORY + '/static/images')
        app.add_static_files('/static/videos', GC.WINDOWS_CODE_DIRECTORY + '/static/videos')
    else:
        print("ERROR: Running on an unknown operating system")
        quit()

    db = Database()

    config = dotenv_values()
    username = config['SENSE_USERNAME']
    password = config['SENSE_PASSWORD']
    sense.authenticate(username, password)

    #TODO REMOVE Since not used ui.timer(GC.UI_UPDATE_TIME, lambda: check_ui_state_machine())
    if GC.DEBUG_STATEMENTS_ON: ui.timer(10, lambda: sense_updating(db, 'DEV'))           # Call every 10 seconds to speed up testing
    ui.timer(GC.SENSE_UPDATE_TIME, lambda: sense_updating(db, 'PROD'))                   # Limit to once every 20 mins to not hit API limits

    logo = ui.image('static/images/DollarGeneralEnergyLogo.png').classes('w-96 m-auto')

    graph = ui.html().classes("self-center")
    graph.visible = False

    calendarElement = ui.date(value=Database.get_date_time(db), on_change=lambda e: get_date_selected(e.value)).classes('m-auto').style("color: #001b36")
    calendarElement.visible = True

    # Invisible character https://invisibletext.com/#google_vignette
    with ui.row().classes("self-center"):
        searchButton = ui.button(on_click=lambda e: search_button_click(db, selectedView), \
                                 color=GC.DOLLAR_STORE_LOGO_GREEN).classes("relative  h-24 w-64")
        with searchButton:
            searchButton.visible = True
            ui.label('SEARCH ㅤ').style('font-size: 100%; font-weight: 300')
            ui.icon('search')

    with ui.row().classes("self-center"):
        radioButtons = ui.radio(GC.RADIO_BUTTON_VALUES, value=GC.RADIO_BUTTON_VALUES[0], \
                                on_change=lambda e: get_radio_button_state(e.value)).props('inline')
        with radioButtons:
            radioButtons.visible = False

    # Invisible character https://invisibletext.com/#google_vignette
    with ui.row().classes("self-center"):
        closeGraphButton = ui.button(on_click=lambda e: close_graph_button_click(), color="red").classes("relative  h-24 w-32")
        with closeGraphButton:
            closeGraphButton.visible = False
            ui.label('CLOSE ㅤ').style('font-size: 100%; font-weight: 300')
            ui.icon('close')

    ui.run(native=GC.RUN_ON_NATIVE_OS, port=GC.LOCAL_HOST_PORT_FOR_GUI)
