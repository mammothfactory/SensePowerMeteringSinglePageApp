#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__contact__    = "blazes@mfc.us"
__copyright__  = "Copyright 2023"
__license__    = "MIT License"
__status__     = "Development"
__deprecated__ = False
__version__    = "0.1.0"
"""

# Disable PyLint linting messages
# https://pypi.org/project/pylint/
# pylint: disable=line-too-long
# pylint: disable=invalid-name

# Standard Python Libraries
from datetime import datetime, time, timedelta  # Manipulate calendar dates & time objects https://docs.python.org/3/library/datetime.>


# 3rd Party Libraries
from nicegui import ui, app                             # Web base GUI framework
from fastapi import FastAPI                             # Web Server at: uvicorn MainApp:app --reload --port 8000

# Internal Libraries
from Database import Database

import GlobalConstants as GC

def init(fastApiApp: FastAPI) -> None:
    @ui.page('init_setting')
    def init_setting():
        ui.label('Dollar General Energy Cost at 3521 Russel Road')

    token = '3' #load_dotenv()
    ui.run_with(fastApiApp, storage_secret=token)


def set_background(color: str) -> None:
    ui.query('body').style(f'background-color: {color}')


def build_svg_graph(db: Database, selectedDate: str, selectedView: GC) -> str:
    """ Create an 1920 x 1080 graph in HTML / SVG

    Args:
        NONE

    Returns:
        str: Valid HTML to create a time vs Wh line graph
    """
    if (GC.DEBUG_STATEMENTS_ON): print("BUILDING GRAPH")
    
    if selectedDate != None:
        year, month, day = map(int, selectedDate.split('-'))
    else:
        current_date = datetime.now()
        year, month, day = current_date.year, current_date.month, current_date.day

    selectedDateObject = datetime(year, month, day)

    days = [selectedDateObject]

    for nextDayNumber in range(1, 7):
        days.append(selectedDateObject + timedelta(days=nextDayNumber))

    # We only use the first 10 characters, none of the time info
    day1 = days[0].isoformat(timespec="minutes")[0:10]
    valueDay1 = 100
    #valueDay1 = db.
    day2 = days[1].isoformat(timespec="minutes")[0:10]
    day3 = days[2].isoformat(timespec="minutes")[0:10]
    day4 = days[3].isoformat(timespec="minutes")[0:10]
    day5 = days[4].isoformat(timespec="minutes")[0:10]
    day6 = days[5].isoformat(timespec="minutes")[0:10]
    day7 = days[6].isoformat(timespec="minutes")[0:10]

    scalingFactor = 1000
    
    if (GC.DEBUG_STATEMENTS_ON): print(f"View selected was: {selectedView}")

    return f'''
    <svg width="700" height={scalingFactor*(GC.MAX_GRAPH_PERCENTAGE/100)} viewBox="-100 -50 800 1100" xmlns="http://www.w3.org/2000/svg">
        <title>Energy Consumption Bar Graph</title>

        <!-- Draw the data points first so that the axis black lines are visible -->
        <line x1="50"  y1="1000" x2="50" y2={valueDay1-GC.MAX_GRAPH_PERCENTAGE} stroke="red" stroke-width="100"/>
        <line x1="150" y1="1000" x2="150" y2="350" stroke="green" stroke-width="100"/>
        <line x1="250" y1="1000" x2="250" y2="250" stroke="red" stroke-width="100"/>
        <line x1="350" y1="1000" x2="350" y2="150" stroke="black" stroke-width="100"/>
        <line x1="450" y1="1000" x2="450" y2="50" stroke="red" stroke-width="100"/>
        <line x1="550" y1="1000" x2="550" y2="0" stroke="green" stroke-width="100"/>
        <line x1="650" y1="1000" x2="650" y2="650" stroke="red" stroke-width="100"/>

        <!-- X-Axis Labels -->
        <text x="50"  y="1050" text-anchor="middle">{day1}</text>
        <text x="150" y="1050" text-anchor="middle">{day2}</text>
        <text x="250" y="1050" text-anchor="middle">{day3}</text>
        <text x="350" y="1050" text-anchor="middle">{day4}</text>
        <text x="450" y="1050" text-anchor="middle">{day5}</text>
        <text x="550" y="1050" text-anchor="middle">{day6}</text>
        <text x="650" y="1050" text-anchor="middle">{day7}</text>

        <!-- Y-Axis Labels -->
        <text x="-10" y="0" text-anchor="end"> 1 kWh</text>
        <text x="-10" y="100"  text-anchor="end">0.90 kWh</text>
        <text x="-10" y="200"  text-anchor="end">0.80 kWh</text>
        <text x="-10" y="300"  text-anchor="end">0.70 kWh</text>
        <text x="-10" y="400"  text-anchor="end">0.60 kWh</text>
        <text x="-10" y="500"  text-anchor="end">0.50 kWh</text>
        <text x="-10" y="600"  text-anchor="end">0.40 kWh</text>
        <text x="-10" y="700"  text-anchor="end">0.30 kWh</text>
        <text x="-10" y="800"  text-anchor="end">0.20 kWh</text>
        <text x="-10" y="900"  text-anchor="end">0.10 kWh</text>
        <text x="-10" y="1000" text-anchor="end">0.00 kWh</text>

        <!-- x-axis -->
        <line x1="0" y1="1000" x2="700" y2="1000" stroke="black" stroke-width="3"/>
        <!-- y-axis -->
        <line x1="0" y1="0" x2="0" y2="1000" stroke="black" stroke-width="3"/>

    </svg>
    '''

async def update_graph(direction: int, sanitizedID: str):
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


if __name__ == "__main__":
    print("1")
    app = FastAPI()
    init(app)
    print("2")
