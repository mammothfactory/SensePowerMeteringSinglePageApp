#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
 __contact__   = "blazes@mfc.us"
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

app = FastAPI()
totalEnergy = 0                     # Units are kWh
sanitizedInput = ''                 # Default string variable used to search for data
validDate = '2023-12-30T13:45:42'   # Valid datetime object in the  ISO-?? format. Called usin .isoformet() TODO
canUpdateweeklyReportTable = True


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

if __name__ in {"__main__", "__mp_main__"}:
    #UserInterface.init(app)

    db = Database()
    db.setup_tables()
    #command = ['python3', 'pagekite.py', f'{GC.LOCAL_HOST_PORT_FOR_GUI}', 'timetracker.pagekite.me']

    ui.timer(GC.LABEL_UPDATE_TIME, lambda: clockedInLabel.set_visibility(False))
    ui.timer(GC.LABEL_UPDATE_TIME, lambda: clockedOutLabel.set_visibility(False))
    ui.timer(GC.LABEL_UPDATE_TIME, lambda: tryAgainLabel.set_visibility(False))
    ui.timer(GC.LABEL_UPDATE_TIME, lambda: UserInterface.set_background('white'))
    ui.timer(GC.DATABASE_WEEKLY_REPORT_UPDATE_TIME, lambda: generate_report())
    ui.timer(GC.CLOCK_UPDATE_TIME, lambda: UserInterface.build_svg_graph())

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


