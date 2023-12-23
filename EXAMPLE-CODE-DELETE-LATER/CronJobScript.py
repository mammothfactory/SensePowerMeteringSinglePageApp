import ManualTimeCalculations
import GlobalConstants as GC
import subprocess
from time import sleep

import schedule

print("Testing CronJob Script")

def is_sunday_pass_2330(testing=False):
    if testing:
        return True
    
    # Get the current date and time
    now = ManualTimeCalculations.get_date_time()

    # Check if today is Sunday (6 corresponds to Sunday)
    if now.weekday() == GC.SUNDAY:
        # Check if the current time is past 11:30 PM (23:30)
        if now.hour > 23 and now.minute >= 30:
            return True

    return False

def job():
    if is_sunday_pass_2330():
        print("Running your script on a Sunday past 11:30 PM.")
        command = ['python3', 'ManualTimeCalculations.py']
        calcProcess = subprocess.Popen(command).pid
        print(f'PID = {calcProcess}')
        
        sleep(3)  # Pause to give ManualTimeCalculations.py to write and close the three .csv files below
            
        dates = ManualTimeCalculations.create_dates()
        filenames = ['', '', '']
        filenames[0] = dates[0] + '_' + dates[6] + '_LaborerTimeReport.csv'
        filenames[1] = dates[0] + '_' + dates[6] + '_CheckOutTimes.csv'
        filenames[2] = dates[0] + '_' + dates[6] + '_CheckInTimes.csv'
        
        for file in filenames:
            #command = ['mv', file, '/Users/venus/Excel Time Card Reports'] # Used when run on Blaze's Mac Book Pro
            command = ['mv', file, '/TimeCardReports']                            # Used when run on Linodes/TimeTracker-Debian-US-Southeast instance

            moveProcess = subprocess.Popen(command).pid
            print(f'PID = {moveProcess}')
        
    else:
        print("Not running the script at this time.")
    
    
schedule.every(20).minutes.do(job)
schedule.every().day.at("23:31").do(job)
schedule.every().sunday.at("23:31", "America/Chicago").do(job)

while True:
    schedule.run_pending()
    sleep(1)