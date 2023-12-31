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

# Standard Python libraries
import sys                                      # Used to determine which operating system this code is running on
from datetime import datetime, time, timedelta 	# Manipulate calendar dates & time objects https://docs.python.org/3/library/datetime.html

# 3rd party libraries
from fastapi import FastAPI

# Browser based GUI framework to build and display a user interface onmobile, PC, and Mac
# https://nicegui.io/
from nicegui import app, ui
from nicegui.events import MouseEventArguments

# Internally developed modules
import GlobalConstants as GC                    # Useful global constants
from Database import Database                   # Store non-Personally Identifiable Information in local (to server) SQlite database
import UserInterface

# Global Variables
api = FastAPI()
currentGuiState = 0                     # State Machine number for the GUI layout
dateSelected = '' #datetime()           # Date selcted with left mouse click from the ui.date() calendar element
totalEnergy = 0                         # Units are kWh
sanitizedInput = ''                     # Default string variable used to search for data
validDate = '2023-12-30T13:45:42'       # Valid datetime object in the  ISO-?? format. Called usin .isoformet() TODO
canUpdateweeklyReportTable = True       # 
toggleButtonIconState = 'switch_left'   #

@app.get('/')
def root():
    return totalEnergy


def generate_report(db):
    """ Generate EXCEL document every monday at 3 am
        Work week starts Sunday at 12:01 am and repeats every 7 days
        Work week ends Saturday at 11:59 pm and repeats every 7 days
        Assumes 12 hour work day at 11 pm if an employee only clocks IN but forgets to clock out
        Back calculates 12 hour work day using the time an employee clocks OUT if no clocking IN exists

        db (sqlite): *.db database file
    """
    currentDateObj = db.get_date_time()
    dayOfWeek = currentDateObj.weekday()
    currentTime = currentDateObj.time()

    if dayOfWeek == GC.MONDAY and (ELEVEN_PM < currentTime and currentTime < THREE_AM):
        canUpdateweeklyReportTable = True
        db.export_table_to_csv(["WeeklyReportTable", "CheckInTable", "CheckOutTable"])


def sync():
    """ Force Syncthing systemd daemon restart
        https://www.youtube.com/watch?v=g-FZCIF0HJw
    """
    #command = ['sudo', 'systemctl', 'restart', 'syncthing@root.service']
    pass


def toggle_button_click(iconState: str):
    global toggleButtonIconState
    #ui.icon('switch_right')

    if iconState == 'switch_left':
        newIconState = 'switch_right'
    else:
        newIconState = 'switch_left'

    toggleButtonIconState = newIconState


def search_button_click(db: Database, startDate: datetime):
    calendarElement.visible = False
    logo.visible = False
    graph.visible = True
    searchButton.visible = False
    closeGraphButton.visible = True
    UserInterface.build_svg_graph(db, startDate)

def close_graph_button_click():
    calendarElement.visible = True
    logo.visible = True
    graph.visible = False
    closeGraphButton.visible = False
    searchButton.visible = True


def check_ui_state_machine():
    """ Simple state machine to describe the GUI
        State 0 means TODO
        State 1 means TODO
        State 2 means TODO
    """
    global currentGuiState

    if calendarElement.visible == True and searchButton.visible == True:
        newState = 0
    elif calendarElement.visible == False and searchButton.visible == False:
        newState = 1
    else:
        newState = 2

    currentGuiState = newState


def get_date_selected(e: str):
    global dateSelected
    dateSelected = e


if __name__ in {"__main__", "__mp_main__"}:
    #UserInterface.init(app)
    ui.colors(primary=GC.DOLLAR_STORE_LOGO_BLUE)

    # Create directory and URL for local storage of images
    if sys.platform.startswith('darwin'):
        app.add_static_files('/static/images', GC.MAC_CODE_DIRECTORY +'/static/images')
        app.add_static_files('/static/videos', GC.MAC_CODE_DIRECTORY + '/static/videos')
    elif sys.platform.startswith('linux'):
        app.add_static_files('/static/images', GC.LINUX_CODE_DIRECTORY + '/static/images')
        app.add_static_files('/static/videos', GC.LINUX_CODE_DIRECTORY + '/static/videos')
    elif sys.platform.startswith('win'):
        print("WARNING: Running Main.py server code on Windows OS is NOT fully supported")
        app.add_static_files('/static/images', GC.WINDOWS_CODE_DIRECTORY + '/static/images')
        app.add_static_files('/static/videos', GC.WINDOWS_CODE_DIRECTORY + '/static/videos')
    else:
        print("ERROR: Running on an unknown operating system")
        quit()

    db = Database()
    db.example_tables()

    ui.timer(GC.UI_UPDATE_TIME, lambda: check_ui_state_machine())
    ui.timer(GC.UI_UPDATE_TIME, lambda: graph.set_content(UserInterface.build_svg_graph(db, dateSelected)))

    logo = ui.image('static/images/DollarGeneralEnergyLogo.png').classes('w-96 m-auto')

    graph = ui.html().classes("self-center")
    graph.visible = False

    calendarElement = ui.date(value=Database.get_date_time(db), on_change=lambda e: get_date_selected(e.value)).classes('m-auto').style("color: #001b36")
    calendarElement.visible = True

    # Invisible character https://invisibletext.com/#google_vignette
    with ui.row().classes("self-center"):
        searchButton = ui.button(on_click=lambda e: search_button_click(db, dateSelected), color=GC.DOLLAR_STORE_LOGO_GREEN).classes("relative  h-24 w-64")
        with searchButton:
            searchButton.visible = True
            ui.label('SEARCH ㅤ').style('font-size: 100%; font-weight: 300')
            ui.icon('search')

    with ui.row().classes("self-center"):
        toggleButton = ui.button(on_click=lambda e: toggle_button_click(toggleButtonIconState), color="red").classes("relative  h-24 w-64")
        toggleButton.visible = False
        with toggleButton:
            ui.label('TOGGLE WEEK & MONTH ㅤ').style("font-size: 100%; font-weight: 300")
            ui.icon(toggleButtonIconState)

    # Invisible character https://invisibletext.com/#google_vignette
    with ui.row().classes("self-center"):
        closeGraphButton = ui.button(on_click=lambda e: close_graph_button_click(), color="red").classes("relative  h-24 w-32")
        with closeGraphButton:
            closeGraphButton.visible = False
            ui.label('CLOSE ㅤ').style('font-size: 100%; font-weight: 300')
            ui.icon('close')

    ui.run(native=GC.RUN_ON_NATIVE_OS, port=GC.LOCAL_HOST_PORT_FOR_GUI)

    #TODO Remove after I no longer need an ui.label example linked to a GUI timer
    #invalidIdLabel = ui.label('ID DE EMPLEADO NO VÁLIDO (INVALID EMPLOYEE ID)').style("color: red; font-size: 150%; font-weight: 300").classes("self-center")
    #invalidIdLabel.visible = False
    #ui.timer(GC.LABEL_UPDATE_TIME, lambda: clockedInLabel.set_visibility(False))
    #clocke dInLabel = ui.label(f'REGISTRO EN (CLOCKED IN)').style("color: green; font-size: 200%; font-weight: 300").classes("self-center")
    #ui.timer(GC.LABEL_UPDATE_TIME, lambda: UserInterface.set_background('white'))

