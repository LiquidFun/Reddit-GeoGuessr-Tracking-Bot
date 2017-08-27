### exclam /usr/bin/env python3

#from CreateTableFromDatabase import getRankingsFromDatabase
import time
from CheckAndPostForSeriesSubmissions import checkNewSubmissions

# Refreshes all other scripts every couple of minutes
def refreshScripts():

    while True:
        try:
            checkNewSubmissions()
        except Exception as e:
            #traceback.print_exc()
            print("Found error, skipping this loop. ")
            print(str(e))
        timeToSleep = 900
        print("Sleeping for " + str(timeToSleep / 60) + " minutes.")
        time.sleep(timeToSleep)
        print("")



if __name__ == '__main__':
    refreshScripts()