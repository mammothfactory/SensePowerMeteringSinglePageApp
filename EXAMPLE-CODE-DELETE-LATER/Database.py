#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__contact__    = "blazes@mfc.us"
__copyright__  = "Copyright 2023"
__license__    = "MIT License"
__status__     = "Development
__deprecated__ = False
__version__    = "0.1.0"
"""

# Disable PyLint linting messages
# https://pypi.org/project/pylint/
# pylint: disable=line-too-long
# pylint: disable=invalid-name

# Standard Python libraries
import sqlite3
	
from datetime import datetime, time, timedelta 	# Manipulate calendar dates & time objects https://docs.python.org/3/library/datetime.html
from time import sleep
import pytz 					                # World Timezone Definitions  https://pypi.org/project/pytz/

import os
import csv

# Internal modules
import GlobalConstants as GC

ELEVEN_PM = time(23, 0, 0)
THREE_AM  = time(3, 0, 0)

class Database:
    
    DEBUGGING = True
    
    """ Store non-Personally Identifiable Information in SQLite database
    """

    def __init__(self):
        """ Constructor to initialize an Database object
        """
        # Connect to the database (create if it doesn't exist)
        self.conn = sqlite3.connect('TimeReport.db')
        self.cursor = self.conn.cursor()

        # Create four tables in TimeReport.db for user name and time logging data storage
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS UsersTable (id INTEGER PRIMARY KEY, employeeId INTEGER, firstName TEXT, lastName TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS CheckInTable (id INTEGER PRIMARY KEY, employeeId INTEGER, timestamp TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS CheckOutTable (id INTEGER PRIMARY KEY, employeeId INTEGER, timestamp TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS WeeklyReportTable (id INTEGER PRIMARY KEY, fullname TEXT, employeeId INTEGER, totalHours INTEGER, day6 INTEGER, day0 INTEGER, day1 INTEGER, day2 INTEGER, day3 INTEGER, day4 INTEGER, day5 INTEGER, inComments TEXT, outComments TEXT)''')
        
        # Create debuging logg
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS DebugLoggingTable (id INTEGER PRIMARY KEY, logMessage TEXT)''')
        
        # Commit the five tables to database
        self.conn.commit()
        
    
    def setup_users(self):
        """ Define initial users for 
        """
        self.insert_users_table("1000", "Erick",    "Maldonado")
        self.insert_users_table("1001", "Dago",     "Reyes Astello")
        self.insert_users_table("1002", "Cesar",    "Rene Cabrera")
        self.insert_users_table("1003", "Adrian",   "Cardenas")
        self.insert_users_table("1004", "Miguel",   "Lopez Perez") 
        self.insert_users_table("1005", "Edgar",    "Maldonado") 
        self.insert_users_table("1006", "German",   "Maranto") 
        self.insert_users_table("1007", "Juan ",    "Antonio") 
        self.insert_users_table("1008", "Victor",   "Mata") 
        self.insert_users_table("1009", "Eric ",    "Mata Vazquez") 
        self.insert_users_table("1010", "David",    "Montoya") 

        self.insert_users_table("1011", "Omar",     "Palomo Galvan")  
        self.insert_users_table("1012", "Nicolas",  "Gomez Perez")
        self.insert_users_table("1013", "Felipe",   "Otero") 
        self.insert_users_table("1014", "Ulises",   "Rodriguez") 
        self.insert_users_table("1015", "Fidencio", "Santiz Lopez") 
        self.insert_users_table("1016", "Nicolas",  "Perez Santiz") 
        self.insert_users_table("1017", "Rigoberto","Savedra") 
        self.insert_users_table("1018", "Jorge",    "Velazquez") 
        self.insert_users_table("1019", "Oscar",    "Cruz Zaleta") 
        self.insert_users_table("1020", "Oscar",    "Rodriguez")

        self.insert_users_table("1021", "Osiel",    "Hernandez")  
        self.insert_users_table("1022", "Elias",    "Castaneda")
        self.insert_users_table("1023", "Thomas",   "Humphrey") 
        self.insert_users_table("1024", "Chase",    "Soliz") 
        self.insert_users_table("1025", "Derrick",  "Lohner") 
    
    def setup_weekly_report(self):
        
        zero = 0
        users = db.query_table("UsersTable")
        
        for data in users:
            employeeID = data[GC.EMPLOYEE_ID_COLUMN_NUMBER]
            name = data[GC.FIRST_NAME_COLUMN_NUMBER] + " " + data[GC.LAST_NAME_COLUMN_NUMBER]
            self.cursor.execute("INSERT INTO WeeklyReportTable (fullname, employeeId, totalHours, day6, day0, day1, day2, day3, day4, day5, inComments, outComments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, employeeID, zero, zero, zero, zero, zero, zero, zero, zero, "Missed: ", "Missed:"))
        
    def commit_changes(self):
        """ Commit data inserted into a table to the *.db database file 
        """
        self.conn.commit()


    def close_database(self):
        """ Close database to enable another sqlite3 instance to query a *.db database
        """
        self.conn.close()


    def get_date_time(self) -> datetime:
        """ Get date and time in Marianna, FL timezone, independent of location on server running code

        Returns:
            Datetime: 
        """
        tz = pytz.timezone('America/Chicago')
        zulu = pytz.timezone('UTC')
        now = datetime.now(tz)
        if now.dst() == timedelta(0):
            now = datetime.now(zulu) - timedelta(hours=6)
            #print('Standard Time')

        else:
            now = datetime.now(zulu) - timedelta(hours=5)
            #print('Daylight Savings')   
            
        return now 


    def query_table(self, tableName: str):
        """ Return every row of a table from a *.db database

        Args:
            tableName (String): Name of table in database to query

        Returns:
            List: Tuples from a table, where each row in table is a tuple length n
        """
        sqlStatement = f"SELECT * FROM {tableName}"
        self.cursor.execute(sqlStatement)

        result = self.cursor.fetchall()

        return result
    
    
    def insert_users_table(self, id: int, first: str, last: str):
        """ Insert employee ID, first name, and last name first initial into the User Table if employee ID is unqiue, otherwise update name
        
        Args:
            id (int): Employee ID (from 1 to 9999) linked to internal email (e.g. 9000@mammothfactory.co)
            first (str): Full first name (or nickname) of employee
            last (str): The first initial of employee last name to make data less Personally Identifiable Information 
        """
        results = self.search_users_table(id)

        if len(results) > 0:
            idPrimaryKeyToUpdate = results[0][0]
            self.cursor.execute("UPDATE UsersTable SET employeeId = ?, firstName = ?, lastName = ? WHERE id = ?", (id, first, last, idPrimaryKeyToUpdate))
        else:
            self.cursor.execute("INSERT INTO UsersTable (employeeId, firstName, lastName) VALUES (?, ?, ?)", (id, first, last))

        self.commit_changes()

    
    def insert_check_in_table(self, id: int) -> tuple:
        """ Insert date and time (to current mintue) into CheckInTable of database
            https://en.wikipedia.org/wiki/ISO_8601

        Args:
            id (int): Employee ID (from 1 to 9999) linked to internal email (e.g. 9000@mammothfactory.co)
        """
        data = self.query_table("CheckInTable")
        result = list(filter(lambda t: t[GC.EMPLOYEE_ID_COLUMN_NUMBER] == id, data))
        if GC.DEBUG_STATEMENTS_ON:  print(f'EMPLOYEE ID FILTER: {result}')

        isoString = '?'
        currentDateTime = self.get_date_time().isoformat(timespec="minutes")
        
        try:
            storedIsoString = result[0][GC.TIMESTAMP_COLUMN_NUMBER]
            if GC.DEBUG_STATEMENTS_ON:  print(f'ISO DateTime: {storedIsoString}')
        
        except IndexError:
            if GC.DEBUG_STATEMENTS_ON: print(f'INSERTING {id} since this employee ID has NOT clocked IN TODAY')
            self.cursor.execute("INSERT INTO CheckInTable (employeeId, timestamp) VALUES (?, ?)", (id, currentDateTime))
            self.commit_changes()
            return '',''

        finally:
            nameResults= []
            nameResults = self.search_users_table(str(id))
            if len(nameResults) > 0:
                englishError = f'{nameResults[0][GC.FIRST_NAME_COLUMN_NUMBER]} {nameResults[0][GC.LAST_NAME_COLUMN_NUMBER]} you already clocked in today'
                spanishError = f'{nameResults[0][GC.FIRST_NAME_COLUMN_NUMBER]} {nameResults[0][GC.LAST_NAME_COLUMN_NUMBER]} ya has fichado hoy'
                return englishError, spanishError
            else:
                return '',''


    def insert_check_out_table(self, id: int) -> tuple:
        """ Insert date and time (to current mintue) into CheckOutTable of database
            https://en.wikipedia.org/wiki/ISO_8601

        Args:
            id (int): Employee ID (from 1 to 9999) linked to internal email (e.g. 9000@mammothfactory.co)
        """
        data = self.query_table("CheckOutTable")
        result = list(filter(lambda t: t[GC.EMPLOYEE_ID_COLUMN_NUMBER] == id, data))
        if GC.DEBUG_STATEMENTS_ON:  print(f'EMPLOYEE ID FILTER: {result}')

        isoString = '?'
        currentDateTime = self.get_date_time().isoformat(timespec="minutes")
        
        try:
            storedIsoString = result[0][GC.TIMESTAMP_COLUMN_NUMBER]
            if GC.DEBUG_STATEMENTS_ON:  print(f'ISO DateTime: {storedIsoString}')
            
        except IndexError:
            if GC.DEBUG_STATEMENTS_ON: print(f'INSERTING {id} since this employee ID has NOT clocked OUT TODAY')
            self.cursor.execute("INSERT INTO CheckOutTable (employeeId, timestamp) VALUES (?, ?)", (id, currentDateTime))
            self.commit_changes()
            return '',''

        finally:
            nameResults = []
            nameResult = self.search_users_table(str(id))
            if len(nameResults) > 0:
                englishError = f'{nameResults[0][GC.FIRST_NAME_COLUMN_NUMBER]} {nameResults[0][GC.LAST_NAME_COLUMN_NUMBER]}  you already clocked out today'
                spanishError = f'{nameResults[0][GC.FIRST_NAME_COLUMN_NUMBER]} {nameResults[0][GC.LAST_NAME_COLUMN_NUMBER]}  ya saliste hoy'
                return englishError, spanishError
            else:
                return '',''


    def insert_debug_logging_table(self, debugText: str):
        """ 

        Args:
            debugText (str): ERROR: or WARNING: text message to log 
        """
        self.cursor.execute("INSERT INTO DebugLoggingTable (logMessage) VALUES (?)", (debugText,))
        self.commit_changes()
        

    def search_users_table(self, searchTerm: str):
        """ Search UsersTable table for every occurrence of a string

        Args:
            searchTerm (str): _description_

        Returns:
            List: Of Tuples from a UsersTable, where each List item is a row in the table containing the exact search term
        """
        self.cursor.execute("SELECT * FROM UsersTable WHERE employeeId LIKE ?", ('%' + str(searchTerm) + '%',))
        results = self.cursor.fetchall()

        return results

    # NO CURRENTLY USED!!! See ManualTImeCalculations.py to see now .csv report are generated
    def insert_weekly_report_table(self, id: int, date: datetime):
        """ Build a table using the following rules:
        

        Args:
            id (int): Employee ID
            dateToCalulate (datetime): _description_
        """
        
        try:
            # Get the day of the week (0=Monday, 1=Tuesday, ..., 6=Sunday)
            dayOfWeek = date.weekday()
            if Database.DEBUGGING: 
                dayOfWeek = GC.SUNDAY
                #currentTime = time(22, 45, 0)
                #currentTime = time(23, 22, 0)
                #currentTime = time(23, 59, 0)
                #currentTime = time(24, 0, 0)
                #currentTime = time(1, 2, 0)
                #currentTime = time(2, 59, 0)
                #currentTime = time(3, 11, 0)
            
            dailyHours = self.calculate_time_delta(id, date) 
            
            results = self.search_users_table(id)
            if len(results) > 0:
                idPrimaryKeyToUpdate = results[0][0]
                
                if dayOfWeek == GC.SUNDAY: 
                    self.cursor.execute("UPDATE WeeklyReportTable SET day6 = ? WHERE id = ?", (dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.MONDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET day0 = ? WHERE id = ?", (dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.TUESDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET day1 = ? WHERE id = ?", (dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.WEDNESDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET day2 = ? WHERE id = ?", (dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.THURSDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET day3 = ? WHERE id = ?", (dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.FRIDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET day4 = ? WHERE id = ?", (dailyHours, idPrimaryKeyToUpdate))
                elif dayOfWeek == GC.SATURDAY:
                    self.cursor.execute("UPDATE WeeklyReportTable SET day5 = ? WHERE id = ?", (dailyHours, idPrimaryKeyToUpdate))

                data = self.query_table("WeeklyReportTable")
                if data ==  None:
                    pass
                else:
                    totalHours = sum(data[idPrimaryKeyToUpdate-1][GC.SUNDAY_COLUMN_NUMBERS:GC.SATURDAY_COLUMN_NUMBERS+1])
                    xComments = data[idPrimaryKeyToUpdate-1][GC.IN_COMMENTS_COLUMN_NUMBERS:GC.OUT_COMMENTS_COLUMN_NUMBERS+1]
                    self.cursor.execute("UPDATE WeeklyReportTable SET totalHours = ? WHERE id = ?", (round(totalHours, 2), idPrimaryKeyToUpdate))
                    
                    data = self.query_table("DebugLoggingTable")
                    finalResult = [item for item in data if str(id) in item[1]]
                    dateToCalulate = date.isoformat(timespec="minutes")[0:10]
                    dayOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

                
                if finalResult[0][GC.LOG_MESSAGE_COLUMN_NUMBER].endswith(dateToCalulate):
                    newInText = xComments[0][0:] + " " + dayOfWeek[date.weekday()]
                    newOutText = xComments[1][0:] + " " + dayOfWeek[date.weekday()]
                    print(f'Found ID {id} with {dateToCalulate} date')
                    
                    self.cursor.execute("UPDATE WeeklyReportTable SET inComments = ? WHERE id = ?", (newInText, idPrimaryKeyToUpdate))
                    self.cursor.execute("UPDATE WeeklyReportTable SET outComments = ? WHERE id = ?", (newOutText, idPrimaryKeyToUpdate))

            else:
                print("INVALID USER ID ???")
                    
        except ValueError:
            self.insert_debug_logging_table(f'Invalid date format when generating weekly report on {date}')
            
        except IndexError:
            print("INVALID USER ID")
            
        finally:
            self.commit_changes()

    
    def calculate_time_delta(self, id: int, date: datetime) -> float:
        """ Calculate hours an employee ID worked on a specific date

            Default to 0 hours if employee forgets to both clock IN and clock OUT, otherwise default to 12 hours if employee only performs one on the actions  

        Args:
            id (int): Employee ID
            dateToCalulate (datetime): ISO-8601 date (e.g. "2023-08-22")

        Returns:
            float: Decimals hours between check in and check out time for a specific employee ID on a specific date
        """
        clockedIn = True
        clockedOut = True
        
        data = self.query_table("CheckInTable")
        result = list(filter(lambda t: t[GC.EMPLOYEE_ID_COLUMN_NUMBER] == id, data))
        dateToCalulate = date.isoformat(timespec="minutes")[0:10]
        finalResult = list(filter(lambda t: t[GC.TIMESTAMP_COLUMN_NUMBER].startswith(dateToCalulate), result))
        try:
            checkInIsoString = finalResult[0][GC.TIMESTAMP_COLUMN_NUMBER]
            datetimeCheckInObject = datetime.fromisoformat(checkInIsoString)     # Convert the ISO strings to datetime objects
            
        except IndexError:
            self.insert_debug_logging_table(f'Employee ID #{id} never clocked in on {dateToCalulate}')
            clockedIn = False
            datetimeCheckInObject = None

        data = self.query_table("CheckOutTable")
        result = list(filter(lambda t: t[GC.EMPLOYEE_ID_COLUMN_NUMBER] == id, data))
        finalResult = list(filter(lambda t: t[GC.TIMESTAMP_COLUMN_NUMBER].startswith(dateToCalulate), result))
        try:
            checkOutIsoString = finalResult[0][GC.TIMESTAMP_COLUMN_NUMBER]
            datetimeCheckOutObject = datetime.fromisoformat(checkOutIsoString)   # Convert the ISO strings to datetime objects
            
        except IndexError:
            self.insert_debug_logging_table(f'Employee ID #{id} never clocked out on {dateToCalulate}')
            clockedOut = False
            datetimeCheckOutObject = None

        elaspedHours = 0
        if(not clockedIn and not clockedOut):
            elaspedHours = 0.0
        elif(clockedIn and not clockedOut):
            elaspedHours = 12.0
        elif(not clockedIn and not clockedOut):
            elaspedHours = 12.0
        else:              
            if datetimeCheckInObject and datetimeCheckOutObject:
                # Perform the absolute value subtraction (timeDeltaObject is NEVER negative)
                timeDeltaObject = datetimeCheckOutObject - datetimeCheckInObject
                elaspedSeconds = timeDeltaObject.seconds
                elaspedHours = elaspedSeconds / 3600.0

        return elaspedHours
    
    
    def export_table_to_csv(self, tableNames: list):
        """ Creates a filename assuming that the date that this code runs is a Monday

        Args:
            tableNames (list): List of string table names in the database to convert
        """
        for table in tableNames:

            # Fetch data from the table
            data = self.query_table(table)
            
            if len(data) == 0:
                self.insert_debug_logging_table(f'No table named {table} when converting table to CSV in Database.export_table_to_csv() function at {self.get_date_time()}')
                
            else:
                # Create a .csv filename base on (Monday - 8 days) to (Monday - 2 days) to create for example 2023-08-01_2023-08-07_LaborerTimeReport
                lastSunday = (self.get_date_time() - timedelta(days=8)).isoformat(timespec="minutes")[0:10]
                lastSaturday = (self.get_date_time() - timedelta(days=2)).isoformat(timespec="minutes")[0:10]
                
                currentDirectory = os.getcwd()
                nextDirectory = os.path.join(currentDirectory, 'TimeCardReports')
                if not os.path.exists(nextDirectory):
                    os.makedirs(nextDirectory)
                
                if table == "WeeklyReportTable":
                    columnNames = ["Full Name", "Employee ID", "Total Hours", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Check In Comments", "Check Out Comments"]
                    outputFilename = lastSunday + "_" + lastSaturday  + "_LaborerTimeReport.csv"  
                    filePath = os.path.join(nextDirectory, outputFilename)
                    
                    with open(filePath, 'w', newline='') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow(columnNames[0:12])
                        for row in data:
                            csv_writer.writerow(row[1:])
                            
                    csvfile.close()
                    
                elif table == "CheckInTable":
                    columnNames = ["Full Name", "Employee ID", "Clock IN Timestamp"]
                    outputFilename = lastSunday + "_" + lastSaturday  + "_ClockInTimes.csv"
                    filePath = os.path.join(nextDirectory, outputFilename)

                    with open(filePath, 'w', newline='') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow(columnNames[0:4])
                        for row in data:
                            csv_writer.writerow(row[1:])
                            
                    csvfile.close()
                        
                elif table == "CheckOutTable":
                    columnNames = ["Full Name", "Employee ID", "Clock OUT Timestamp"]
                    outputFilename = lastSunday + "_" + lastSaturday  + "_ClockOutTimes.csv" 
                    filePath = os.path.join(nextDirectory, outputFilename)
                    
                    with open(filePath, 'w', newline='') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow(columnNames[0:4])
                        for row in data:
                            csv_writer.writerow(row[1:])
                            
                    csvfile.close()
                
                else:
                    print(f'Table Name {table} conversion not implemented')
                 
    def is_date_between(startDatetimeObj, endDatetimeObj, dateToCheck) -> bool:
        return startDatetimeObj <= dateToCheck <= endDatetimeObj

if __name__ == "__main__":
    canUpdateweeklyReportTable = True   #TODO REMOVE AFTER Main.generate_report() and Main.update_weekly_report_table() is tested
    print("Testing Database.py")

    db = Database()
    
    """
    db.setup_users()
    db.setup_weekly_report()    
    checkInErrors = db.insert_check_in_table(1001)
    print(checkInErrors)
    #sleep(65)
    checkOutErrors = db.insert_check_out_table(1001)
    print(checkOutErrors)
    """
    
    users = db.query_table("UsersTable")
    for data in users:
        employeeID = data[GC.EMPLOYEE_ID_COLUMN_NUMBER]
        
        currentDateObj = datetime(2023, 8, 27, 5, 0, 0) #db.get_date_time()
        dayOfWeek = currentDateObj.weekday()
        currentTime = currentDateObj.time()
        if dayOfWeek == GC.SUNDAY and (ELEVEN_PM < currentTime and currentTime < THREE_AM):
            canUpdateweeklyReportTable = False
            
        if canUpdateweeklyReportTable:
            #print(f'Updating weekly report for ID {employeeID} on {currentDateObj}')
            db.insert_weekly_report_table(employeeID, currentDateObj)

    
    #db.export_table_to_csv(["WeeklyReportTable", "CheckInTable", "CheckOutTable"])
    
    today = db.get_date_time()
    print(f'Hours = {db.calculate_time_delta(1001, today):.4f}')

    databaseSearch = db.search_users_table("1001")
    if len(databaseSearch) > 0:
        print("Found employee ID in database")
        print(databaseSearch)

    db.close_database()
    
