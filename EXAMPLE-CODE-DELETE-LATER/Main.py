#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
 __contact__   = "blazes@mfc.us"
__copyright__  = "Copyright 2023"
__license__    = "MIT License"
__status__     = "Development
__deprecated__ = False
__version__    = "0.0.1"
__doc__        = "Generate a Progressive Web App GUI to log employee check-in and check-out times"
"""

# Disable PyLint linting messages that seem unuseful
# https://pypi.org/project/pylint/
# pylint: disable=invalid-name
# pylint: disable=global-statement

# Standard Python libraries
from datetime import datetime, time, timedelta 	# Manipulate calendar dates & time objects https://docs.python.org/3/library/datetime.html

# Internally developed modules
import GlobalConstants as GC                    # Global constants used across MainHouse.py, HouseDatabase.py, and PageKiteAPI.py
from Database import Database                   # Store non-Personally Identifiable Information of employee ID's and timestamps

# Browser base GUI framework to build and display a user interface mobile, PC, and Mac # https://nicegui.io/
from nicegui import app, ui
from nicegui.events import MouseEventArguments

THREE_AM = time(3, 0, 0)
ELEVEN_PM = time(23, 0, 0)
clock = ui.html().classes("self-center")

sanitizedID = ''
validEmployeeID = ''
canUpdateweeklyReportTable = True


def build_svg() -> str:
    """ Create an 800 x 800 pixel clock in HTML / SVG
        https://de.m.wikipedia.org/wiki/Datei:Station_Clock.svg

    Args:
        NONE

    Returns:
        str: Valid HTML to create an analog clock
    """
    now = db.get_date_time()
    return f'''
    <svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
    <circle cx="200" cy="200" r="180" stroke="black" stroke-width="4" fill="white" />
    <line x1="200" y1="200" x2="200" y2="50" stroke="black" stroke-width="6" transform="rotate({now.minute / 60 * 360} 200 200)" />
    <line x1="200" y1="200" x2="200" y2="100" stroke="black" stroke-width="6" transform="rotate({now.hour / 12 * 360} 200 200)" />
    <circle cx="200" cy="200" r="20" fill="black" />
    
    <!-- Hour marks -->
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(0 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(30 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(60 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(90 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(120 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(150 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(180 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(210 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(240 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(270 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(300 200 200)" />
    <line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(330 200 200)" />
    </svg>
    '''


async def clock_x(direction: int, sanitizedID: str):
    """ Perform database insert

    Args:
        direction (CONSTANT int):Define function as clock IN or clock OUT method
        sanitizedID (str): Global sanitized number entered into Number text  box
    """

    if invalidIdLabel.visible == False and len(sanitizedID) == GC.VALID_EMPLOYEE_ID_LENGTH:
        if direction == GC.CLOCK_IN:
            clockedInLabel.set_text(f'{sanitizedID} - REGISTRO EN (CLOCKED IN)')
            clockedInLabel.visible = True
            db.insert_check_in_table(sanitizedID)
            #set_background('grey')
            await ui.run_javascript(f'getElement({inputBox.id}).focus()', respond=False)
        
        elif direction == GC.CLOCK_OUT:
            clockedOutLabel.set_text(f'{sanitizedID} - RELOJ DE SALIDA (CLOCK OUT)')
            clockedOutLabel.visible = True
            db.insert_check_out_table(sanitizedID)
            #set_background('grey')
            await ui.run_javascript(f'getElement({inputBox.id}).focus()', respond=False)

    else:
       tryAgainLabel.visible = True
       set_background('grey')

    inputBox.set_value(None)                          # Clear user input box. Note set_value('') doesn't work :)


def sanitize_employee_id(inputText: str) -> str:
    """ Convert all bad user input to valid ouput and update GUI label visibility to control datatbase writes

    Args:
        inputText (str): Raw user input with possible errors

    Returns:
        str: A string with all blank spaces and non-digit characters removed
    """
    global sanitizedID

    if int(inputText) > 9999 or int(inputText) < 0:
        invalidIdLabel.visible = True
        set_background('grey')
        return 'ID DE EMPLEADO NO VÁLIDO (INVALID EMPLOYEE ID)'
    else:
       invalidIdLabel.visible = False

    if inputText == None:
        sanitizedID = ''
    else:
        sanitizedID = str(int(inputText))

    return sanitizedID


# TODO How do I make sure writes to insert_weekly_report_table doesnt get overwritten before report from last week is generated
def update_weekly_report_table():
    global canUpdateweeklyReportTable
    
    users = db.query_table("UsersTable")
    for data in users:
        employeeID = data[GC.EMPLOYEE_ID_COLUMN_NUMBER]
        
        currentDateObj = db.get_date_time()
        dayOfWeek = currentDateObj.weekday()
        currentTime = currentDateObj.time()
        if dayOfWeek == GC.MONDAY and (ELEVEN_PM < currentTime and currentTime < THREE_AM):
            canUpdateweeklyReportTable = False
            
        if canUpdateweeklyReportTable:
            db.insert_weekly_report_table(employeeID, currentDateObj)


def generate_report():
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


def set_background(color: str) -> None:
    ui.query('body').style(f'background-color: {color}')
 
   
def sync():
    """ Force Syncthing systemd daemon restart
        https://www.youtube.com/watch?v=g-FZCIF0HJw
    """
    #command = ['sudo', 'systemctl', 'restart', 'syncthing@root.service']
    pass


if __name__ in {"__main__", "__mp_main__"}:
    db = Database()
    db.setup_users()
    #command = ['python3', 'pagekite.py', f'{GC.LOCAL_HOST_PORT_FOR_GUI}', 'timetracker.pagekite.me']

    ui.timer(GC.LABEL_UPDATE_TIME, lambda: clockedInLabel.set_visibility(False))
    ui.timer(GC.LABEL_UPDATE_TIME, lambda: clockedOutLabel.set_visibility(False))
    ui.timer(GC.LABEL_UPDATE_TIME, lambda: tryAgainLabel.set_visibility(False))
    ui.timer(GC.LABEL_UPDATE_TIME, lambda: set_background('white'))
    ui.timer(GC.DATABASE_DAILY_REPORT_UPDATE_TIME, lambda: update_weekly_report_table())
    ui.timer(GC.DATABASE_WEEKLY_REPORT_UPDATE_TIME, lambda: generate_report())
    ui.timer(GC.CLOCK_UPDATE_TIME, lambda: clock.set_content(build_svg()))

    invalidIdLabel = ui.label('ID DE EMPLEADO NO VÁLIDO (INVALID EMPLOYEE ID)').style("color: red; font-size: 150%; font-weight: 300").classes("self-center")
    invalidIdLabel.visible = False

    inputBox = ui.number(label='Ingrese su identificación de empleado', placeholder='Enter your Employee ID', value=None, \
                        format='%i', \
                        step='1000', \
                        on_change=lambda e: invalidIdLabel.set_text(sanitize_employee_id(e.value)), \
                        validation={'ID DE EMPLEADO NO VÁLIDO (INVALID EMPLOYEE ID)': lambda value: int(sanitizedID) <= 9999})

    inputBox.classes("self-center").style("padding: 40px 0px; width: 600px; font-size: 30px;").props('clearable')

    
    # Invisible character https://invisibletext.com/#google_vignette
    with ui.row().classes("self-center"):
        with ui.button(on_click=lambda e: clock_x(GC.CLOCK_IN, sanitizedID), color="green").classes("relative  h-24 w-64"):
            ui.label('RELOJ EN (CLOCK IN) ㅤ').style('font-size: 90%; font-weight: 300')
            ui.icon('login')

        with ui.button(on_click=lambda e: clock_x(GC.CLOCK_OUT, sanitizedID), color="red").classes("relative  h-24 w-64"):
            ui.label('RELOJ DE SALIDA (CLOCK OUT) ㅤ').style("font-size: 90%; font-weight: 300")
            ui.icon('logout')

    clockedInLabel = ui.label(f'{validEmployeeID} - REGISTRO EN (CLOCKED IN)').style("color: green; font-size: 200%; font-weight: 300").classes("self-center")
    clockedOutLabel = ui.label(f'{validEmployeeID} - FINALIZADO (CLOCKED OUT)').style("color: red; font-size: 200%; font-weight: 300").classes("self-center")
    tryAgainLabel = ui.label('INTENTAR OTRA VEZ (TRY AGAIN)').style("color: red; font-size: 200%; font-weight: 300").classes("self-center")

    ui.run(native=GC.RUN_ON_NATIVE_OS, port=GC.LOCAL_HOST_PORT_FOR_GUI)
