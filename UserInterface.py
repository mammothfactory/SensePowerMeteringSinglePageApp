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

def get_graph_value_per_day(db, date):
    date = datetime.fromisoformat(date).strftime('%Y-%m-%d').replace("-0", "-")
    watthours_per_day = db.get_daily_watthours(date)
    graph_value_per_day = float(watthours_per_day)/7000.0*1000.0 ## 7000 and 1000 must be replaced with Global constants
    return graph_value_per_day

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
    value_day1 = get_graph_value_per_day(db,day1)
    day2 = days[1].isoformat(timespec="minutes")[0:10]
    value_day2 = get_graph_value_per_day(db,day2)
    day3 = days[2].isoformat(timespec="minutes")[0:10]
    value_day3 = get_graph_value_per_day(db,day3)
    day4 = days[3].isoformat(timespec="minutes")[0:10]
    value_day4 = get_graph_value_per_day(db,day4)
    day5 = days[4].isoformat(timespec="minutes")[0:10]
    value_day5 = get_graph_value_per_day(db,day5)
    day6 = days[5].isoformat(timespec="minutes")[0:10]
    value_day6 = get_graph_value_per_day(db,day6)
    day7 = days[6].isoformat(timespec="minutes")[0:10]
    value_day7 = get_graph_value_per_day(db,day7)

    scalingFactor = 1000
    graph_height = scalingFactor*(GC.MAX_GRAPH_PERCENTAGE/100)
    
    if (GC.DEBUG_STATEMENTS_ON): print(f"View selected was: {selectedView}")

    if selectedView == 'WEEK VIEW':
        return f'''
            <svg width="700" height={graph_height} viewBox="-100 -50 800 1100" xmlns="http://www.w3.org/2000/svg">
                <title>Weekly Energy Consumption Bar Graph</title>
        
                <!-- Draw the data points first so that the axis black lines are visible -->
                <line x1="50"  y1="1000" x2="50"  y2={graph_height-value_day1}  stroke="grey"   stroke-width="100"/>
                <line x1="150" y1="1000" x2="150" y2={graph_height-value_day2}  stroke="green"  stroke-width="100"/>
                <line x1="250" y1="1000" x2="250" y2={graph_height-value_day3}  stroke="blue"   stroke-width="100"/>
                <line x1="350" y1="1000" x2="350" y2={graph_height-value_day4}  stroke="black"  stroke-width="100"/>
                <line x1="450" y1="1000" x2="450" y2={graph_height-value_day5}  stroke="yellow" stroke-width="100"/>
                <line x1="550" y1="1000" x2="550" y2={graph_height-value_day6}  stroke="green"  stroke-width="100"/>
                <line x1="650" y1="1000" x2="650" y2={graph_height-value_day7}  stroke="orange" stroke-width="100"/>
        
                <!-- X-Axis Labels -->
                <text x="50"  y="1050" text-anchor="middle">{day1}</text>
                <text x="150" y="1050" text-anchor="middle">{day2}</text>
                <text x="250" y="1050" text-anchor="middle">{day3}</text>
                <text x="350" y="1050" text-anchor="middle">{day4}</text>
                <text x="450" y="1050" text-anchor="middle">{day5}</text>
                <text x="550" y="1050" text-anchor="middle">{day6}</text>
                <text x="650" y="1050" text-anchor="middle">{day7}</text>
        
                <!-- Y-Axis Labels -->
                <text x="-10" y="0"       text-anchor="end">7 kWh</text>
                <text x="-10" y="142.85"  text-anchor="end">6 kWh</text>
                <text x="-10" y="285.70"  text-anchor="end">5 kWh</text>
                <text x="-10" y="428.55"  text-anchor="end">4 kWh</text>
                <text x="-10" y="571.40"  text-anchor="end">3 kWh</text>
                <text x="-10" y="714.25"  text-anchor="end">2 kWh</text>
                <text x="-10" y="857.1"   text-anchor="end">1 kWh</text>
                <text x="-10" y="1000"    text-anchor="end">0 kWh</text>
           
                <!-- X-axis Line -->
                <line x1="0" y1="1000" x2="700" y2="1000" stroke="black" stroke-width="3"/>
                
                <!-- Y-axis Line -->
                <line x1="0" y1="0" x2="0" y2="1000" stroke="black" stroke-width="3"/>
        
            </svg>
        '''
        
    if selectedView == 'MONTH VIEW':
        SHOW_NO_DATA = 0
        return f'''
            <svg width="700" height={graph_height} viewBox="-100 -50 800 1100" xmlns="http://www.w3.org/2000/svg">
                <title>Monthly Energy Consumption Bar Graph</title>
        
                <!-- Draw the data points first so that the axis black lines are visible -->
                <line x1="50"  y1="1000" x2="50"  y2={graph_height-SHOW_NO_DATA}  stroke="grey"   stroke-width="100"/>
                <line x1="150"  1="1000" x2="150" y2={graph_height-value_day1}    stroke="green"  stroke-width="100"/>
                <line x1="250" y1="1000" x2="250" y2={graph_height-value_day2}    stroke="blue"   stroke-width="100"/>
                <line x1="350" y1="1000" x2="350" y2={graph_height-SHOW_NO_DATA}  stroke="black"  stroke-width="100"/>
                <line x1="450" y1="1000" x2="450" y2={graph_height-value_day3}    stroke="yellow" stroke-width="100"/>
                <line x1="550" y1="1000" x2="550" y2={graph_height-value_day4}    stroke="green"  stroke-width="100"/>
                <line x1="650" y1="1000" x2="650" y2={graph_height-SHOW_NO_DATA}  stroke="orange" stroke-width="100"/> 
        
                <!-- X-Axis Labels with 50, 350, and 650 left blank on purpose to center data -->
                <text x="150" y="1050" text-anchor="middle">1st Week</text>
                <text x="250" y="1050" text-anchor="middle">2nd Week</text>
                <text x="450" y="1050" text-anchor="middle">3rd Week</text>
                <text x="540" y="1050" text-anchor="middle">4th Week</text>
          
                <!-- Y-Axis Labels COPY OF WEEK VIEW ABOVE -->
                <text x="-10" y="0"       text-anchor="end">49 kWh</text>
                <text x="-10" y="142.85"  text-anchor="end">42 kWh</text>
                <text x="-10" y="285.70"  text-anchor="end">35 kWh</text>
                <text x="-10" y="428.55"  text-anchor="end">28 kWh</text>
                <text x="-10" y="571.40"  text-anchor="end">21 kWh</text>
                <text x="-10" y="714.25"  text-anchor="end">14 kWh</text>
                <text x="-10" y="857.1"   text-anchor="end">7 kWh</text>
                <text x="-10" y="1000"    text-anchor="end">0 kWh</text>
           
        
                <!-- X-axis Line -->
                <line x1="0" y1="1000" x2="700" y2="1000" stroke="black" stroke-width="3"/>
                
                <!-- Y-axis -->
                <line x1="0" y1="0" x2="0" y2="1000" stroke="black" stroke-width="3"/>
        
            </svg>
        '''


if __name__ == "__main__":
    print("1")
    app = FastAPI()
    init(app)
    print("2")
