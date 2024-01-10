#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders", "Vladyslav Haverdovskyi"]
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

## Standard Python Libraries
from datetime import datetime, time, timedelta    # Manipulate calendar dates & time objects https://docs.python.org/3/library/datetime.>
from pytz import timezone                         # Sync data write time to database no matter where server is located https://pypi.org/project/pytz/

## 3rd party libraries
from nicegui import ui, app                        # Web base GUI framework
from fastapi import FastAPI                        # Web Server at: uvicorn MainApp:app --reload --port 8000

## Internally developed modules
from Database import Database                      # Store non-Personally Identifiable Information in local (to server) SQlite database
import GlobalConstants as GC                       # Useful global constants used across multiple files

# Global variables for cost label
total_kilowatthours_in_weekly_mode = 0.0
total_kilowatthours_in_monthly_mode = 0.0


def init(fastApiApp: FastAPI) -> None:
    @ui.page('init_setting')
    def init_setting():
        ui.label('Dollar General Energy Cost at 3521 Russel Road')

    token = '3' #load_dotenv()
    ui.run_with(fastApiApp, storage_secret=token)


def set_background(color: str) -> None:
    ui.query('body').style(f'background-color: {color}')


def get_graph_value_per_day(watthours_per_day):
    graph_value_per_day = float(watthours_per_day)/7000.0*1000.0   ## TODO 7000 and 1000 must be replaced with Global constants: MAYBE GC.ONE_KILO_PIXELS???
    return graph_value_per_day


def get_graph_value_per_week(weekly_watthours_):
    graph_value_per_week = float(weekly_watthours_)/30000.0*1000.0 ## TODO Why 30K?
    return graph_value_per_week


def build_svg_graph(db: Database, selectedDate: str, selectedView: GC) -> str:
    """ Create an 1920 x 1080 graph in HTML / SVG

    Args:
        NONE

    Returns:
        str: Valid HTML to create a time vs Wh line graph
    """
    daily_graph_values = []
    weekly_graph_values = []

    selected_week_number = datetime.strptime(selectedDate, '%Y-%m-%d').isocalendar()[1]
    selected_date = datetime.fromisoformat(selectedDate).strftime('%Y-%m-%d').replace("-0", "-")

    daily_watthours = db.get_daily_watthours(selected_date)[0]
    weekly_watthours = db.get_weekly_watthours(selected_week_number)[0]

    watthours_array = [o[1] for o in daily_watthours]
    weekly_watthours_array = [o[0] for o in weekly_watthours]

    timestamp_array = [o[0] for o in daily_watthours]
    last_timestamp = timestamp_array[-1]

    if len(watthours_array) < 7:
        for i in range(0, 7-len(watthours_array)):
            watthours_array.append(0)
            additional_timestamp = last_timestamp.split('-')[0]+'-'+last_timestamp.split('-')[1]+'-'+str(int(last_timestamp.split('-')[2])+i+1)
            timestamp_array.append(additional_timestamp)

    for watthours in watthours_array:
        daily_graph_values.append(get_graph_value_per_day(watthours))

    if len(weekly_watthours_array) < 4:
        for i in range(0, 4-len(weekly_watthours_array)):
            weekly_watthours_array.append(0)

    for weekly_watthours_ in weekly_watthours_array:
        weekly_graph_values.append(get_graph_value_per_week(weekly_watthours_))

    scalingFactor = 1000
    graph_height = scalingFactor*(GC.MAX_GRAPH_PERCENTAGE/100)

    global total_kilowatthours_in_weekly_mode, total_kilowatthours_in_monthly_mode
    total_kilowatthours_in_weekly_mode= sum(watthours_array)/1000.0
    total_kilowatthours_in_monthly_mode = sum(weekly_watthours_array)/1000.0

    if (GC.DEBUG_STATEMENTS_ON): print(f"View selected was: {selectedView}")

    if selectedView == 'WEEK VIEW':
        return f'''
            <svg width="700" height={graph_height} viewBox="-100 -50 800 1100" xmlns="http://www.w3.org/2000/svg">
                <title>Weekly Energy Consumption Bar Graph</title>
        
                <!-- Draw the data points first so that the axis black lines are visible -->
                <line x1="50"  y1="1000" x2="50"  y2={graph_height-daily_graph_values[0]} stroke="grey" stroke-width="100"/>
                <line x1="150" y1="1000" x2="150" y2={graph_height-daily_graph_values[1]}  stroke="green" stroke-width="100"/>
                <line x1="250" y1="1000" x2="250" y2={graph_height-daily_graph_values[2]}  stroke="blue" stroke-width="100"/>
                <line x1="350" y1="1000" x2="350" y2={graph_height-daily_graph_values[3]}  stroke="black" stroke-width="100"/>
                <line x1="450" y1="1000" x2="450" y2={graph_height-daily_graph_values[4]}  stroke="yellow" stroke-width="100"/>
                <line x1="550" y1="1000" x2="550" y2={graph_height-daily_graph_values[5]}  stroke="green" stroke-width="100"/>
                <line x1="650" y1="1000" x2="650" y2={graph_height-daily_graph_values[6]}  stroke="orange" stroke-width="100"/>

                <!-- X-Axis Labels -->
                <text x="50"  y="1050" text-anchor="middle">{timestamp_array[0]}</text>
                <text x="150" y="1050" text-anchor="middle">{timestamp_array[1]}</text>
                <text x="250" y="1050" text-anchor="middle">{timestamp_array[2]}</text>
                <text x="350" y="1050" text-anchor="middle">{timestamp_array[3]}</text>
                <text x="450" y="1050" text-anchor="middle">{timestamp_array[4]}</text>
                <text x="550" y="1050" text-anchor="middle">{timestamp_array[5]}</text>
                <text x="650" y="1050" text-anchor="middle">{timestamp_array[6]}</text>
          
                <!-- Y-Axis Labels TODO CHECK MULTIPLYING TEXT BY 154 = GC.WORKING_LED_LIGHTS IS VALID??? -->
                <text x="-10" y="0"       text-anchor="end">1078 kWh</text>
                <text x="-10" y="142.85"  text-anchor="end">924 kWh</text>
                <text x="-10" y="285.70"  text-anchor="end">770 kWh</text>
                <text x="-10" y="428.55"  text-anchor="end">616 kWh</text>
                <text x="-10" y="571.40"  text-anchor="end">462 kWh</text>
                <text x="-10" y="714.25"  text-anchor="end">308 kWh</text>
                <text x="-10" y="857.1"   text-anchor="end">154 kWh</text>
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
                <line x1="50"  y1="1000" x2="50"  y2={graph_height-SHOW_NO_DATA}           stroke="grey"   stroke-width="100"/>
                <line x1="150" y1="1000" x2="150" y2={graph_height-weekly_graph_values[0]} stroke="green"  stroke-width="100"/>
                <line x1="250" y1="1000" x2="250" y2={graph_height-weekly_graph_values[1]} stroke="blue"   stroke-width="100"/>
                <line x1="350" y1="1000" x2="350" y2={graph_height-SHOW_NO_DATA}           stroke="black"  stroke-width="100"/>
                <line x1="450" y1="1000" x2="450" y2={graph_height-weekly_graph_values[2]} stroke="yellow" stroke-width="100"/>
                <line x1="550" y1="1000" x2="550" y2={graph_height-weekly_graph_values[3]} stroke="green"  stroke-width="100"/>
                <line x1="650" y1="1000" x2="650" y2={graph_height-SHOW_NO_DATA}           stroke="orange" stroke-width="100"/>   
        
                <!-- X-Axis Labels with 50, 350, and 650 left blank on purpose to center data -->
                <text x="150" y="1050" text-anchor="middle">1st Week</text>
                <text x="250" y="1050" text-anchor="middle">2nd Week</text>
                <text x="450" y="1050" text-anchor="middle">3rd Week</text>
                <text x="540" y="1050" text-anchor="middle">4th Week</text>
          
                <!-- Y-Axis Labels COPY OF WEEK VIEW ABOVE * 7 TODO CHECK MULTIPLYING TEXT BY 150 IS VALID??? -->
                <text x="-10" y="0"       text-anchor="end">7546 kWh</text>
                <text x="-10" y="142.85"  text-anchor="end">6468 kWh</text>
                <text x="-10" y="285.70"  text-anchor="end">5390 kWh</text>
                <text x="-10" y="428.55"  text-anchor="end">4312 kWh</text>
                <text x="-10" y="571.40"  text-anchor="end">3234 kWh</text>
                <text x="-10" y="714.25"  text-anchor="end">2156 kWh</text>
                <text x="-10" y="857.1"   text-anchor="end">1078 kWh</text>
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
