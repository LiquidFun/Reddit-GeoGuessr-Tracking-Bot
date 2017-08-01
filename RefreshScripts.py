#from CreateTableFromDatabase import getRankingsFromDatabase
import time
from CheckAndPostForSeriesSubmissions import checkNewSubmissions

# Refreshes all other scripts every couple of minutes
def refreshScripts():

    while True:
        checkNewSubmissions()
        timeToSleep = 900
        print("Sleeping for " + str(timeToSleep / 60) + " minutes.")
        time.sleep(timeToSleep)
        print("")



if __name__ == '__main__':
    refreshScripts()