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


# 3rd Party Libraries
from nicegui import ui, app     # Web base GUI framework
from fastapi import FastAPI     # Web Server at: uvicorn MainApp:app --reload --port 8000

# Internal Libraries
from Database import Database


def init(fastApiApp: FastAPI) -> None:
    @ui.page('init_setting')
    def init_setting():
        ui.label('Dollar General Energy Cost at 3521 Russel Road')

    token = '3' #load_dotenv()
    ui.run_with(fastApiApp, storage_secret=token)


def set_background(color: str) -> None:
    ui.query('body').style(f'background-color: {color}')


def build_svg_graph(db: Database, now) -> str:
    """ Create an 1920 x 1080 graph in HTML / SVG

    Args:
        NONE

    Returns:
        str: Valid HTML to create a time vs Wh line graph

    #<!DOCTYPE html>
    #<html>
    #<head>
    #</head>
    #<body>
    #<div id="bar-graph-container"></div>

    #</body>
    #</html>

    """
    return f'''
    <svg width="700" height="1100" viewBox="-100 -50 700 1100" xmlns="http://www.w3.org/2000/svg">
        <title>Energy Consumption Bar Graph</title>

        <!-- Draw the data  points first so that the axis black lines are visible -->
        <line x1="50"  y1="1000" x2="50" y2="0" stroke="red" stroke-width="100"/>
        <line x1="150" y1="1000" x2="150" y2="350" stroke="green" stroke-width="100"/>
        <line x1="250" y1="1000" x2="250" y2="250" stroke="green" stroke-width="100"/>
        <line x1="350" y1="1000" x2="350" y2="150" stroke="green" stroke-width="100"/>
        <line x1="450" y1="1000" x2="450" y2="50" stroke="green" stroke-width="100"/>
        <line x1="550" y1="1000" x2="550" y2="0" stroke="green" stroke-width="100"/>
        <line x1="650" y1="1000" x2="650" y2="650" stroke="green" stroke-width="100"/>

        <!-- X-Axis Labels -->
        <text x="50"  y="1050" text-anchor="middle">Day 1</text>
        <text x="150" y="1050" text-anchor="middle">Day 2</text>
        <text x="250" y="1050" text-anchor="middle">Day 3</text>
        <text x="350" y="1050" text-anchor="middle">Day 4</text>
        <text x="450" y="1050" text-anchor="middle">Day 5</text>
        <text x="550" y="1050" text-anchor="middle">Day 6</text>
        <text x="650" y="1050" text-anchor="middle">Day 7</text>

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
        <line x1="0" y1="1000" x2="700" y2="1000" stroke="black" stroke-width="5"/>
        <!-- y-axis -->
        <line x1="0" y1="0" x2="0" y2="1000" stroke="black" stroke-width="5"/>

    </svg>
    '''

    # GC.BAR_WIDTH = 30
    # GC.MAX_CONSUMPTION = 500
    #<circle cx="200" cy="200" r="180" stroke="black" stroke-width="4" fill="white" />


    #<line x1="200" y1="200" x2="200" y2="100" stroke="black" stroke-width="6" transform="rotate({10 / 12 * 360} 200 200)" />
    #<circle cx="200" cy="200" r="20" fill="black" />

    #<!-- Hour marks -->
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(0 200 200)" />
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(30 200 200)" />
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(60 200 200)" />
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(90 200 200)" />
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(120 200 200)" />
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(150 200 200)" />
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(180 200 200)" />
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(210 200 200)" />
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(240 200 200)" />
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="10" transform="rotate(270 200 200)" />
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(300 200 200)" />
    #<line x1="200" y1="50" x2="200" y2="70" stroke="black" stroke-width="3" transform="rotate(330 200 200)" />


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


def sanitize_weeknumber_date_input(inputText: str) -> str:
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


if __name__ == "__main__":
    print("1")
    app = FastAPI()
    init(app)
    print("2")
