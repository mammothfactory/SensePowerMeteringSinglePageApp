#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__contact__    = "blazes@mfc.us"
__copyright__  = "Copyright 2023"
__license__    = "MIT License"
__status__     = "Development
__deprecated__ = False
__version__    = "0.1.0"
__doc__        = "CONSTANTS for both LiteHouse and Lustron home configurations"
"""


# Physical equipment at Marianna factory 
WORKING_LED_LIGHTS = 154
BROKEN_LED_LIGHTS  = 8
OFF_LED_LIGHTS     = 8
NON_WORKING_LED_LIGHTS = BROKEN_LED_LIGHTS + OFF_LED_LIGHTS


# SQLite Database CONSTANTS
INSTANT_ENERGY_COLUMN_NUMBER = 1
COST_COLUMN_NUMBER = 2
TIMESTAMP_COLUMN_NUMBER =3
TOTAL_ENERGY_COLUMN_NUMBER = 1
WATT_HOUR_COLUMN_NUMBER = 1
WEEK_NUMBER_COLUMN_NUMBER = 2
MONTH_NUMBER_COLUMN_NUMBER = 2
LOG_MESSAGE_COLUMN_NUMBER = 1

# Default file location for code
MAC_CODE_DIRECTORY   = '/Users/venus/GitRepos/SensePowerMeteringSinglePageApp'
LINUX_CODE_DIRECTORY = '/SensePowerMeteringSinglePageApp'
WINDOWS_CODE_DIRECTORY = 'D:/2-WorkStation/2-Upwork-Projects/Recommendation_For_Mammoth/Mammoth/SensePowerMeteringSinglePageApp'


# GUI Display CONSTANTS
DEBUG_STATEMENTS_ON = True
RUN_ON_NATIVE_OS = False
LOCAL_HOST_PORT_FOR_GUI = 8282
DOLLAR_STORE_LOGO_BLUE = '#001B36'
DOLLAR_STORE_LOGO_GREEN = '#8EE511'
MAX_GRAPH_PERCENTAGE = 100                              # Units are in percentage
RADIO_BUTTON_VALUES = ['WEEK VIEW','MONTH VIEW']
FACTORY_ENERGY_COST = 0.11                              # Units are US Dollars

# NiceGUI ui.timer() CONSTANTS
ONE_SECOND = 1                                          # 1 second
ONE_HOUR = ONE_SECOND * 60 * 60                         # 1 hour
CLOCK_UPDATE_TIME = 60 * ONE_SECOND                     # 60 seconds
LABEL_UPDATE_TIME = 4 * ONE_SECOND                      # 4 seconds
DATABASE_DAILY_REPORT_UPDATE_TIME  = 12 * ONE_HOUR      # 12 hours
DATABASE_WEEKLY_REPORT_UPDATE_TIME =  4 * ONE_HOUR      # 4 hours
SENSE_UPDATE_TIME = 1 * ONE_HOUR                # 1 hour
UI_UPDATE_TIME = 0.5 * ONE_HOUR                                    # 30 minutes

# DateTime Object CONSTANTS
MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6
