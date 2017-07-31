#from CreateTableFromDatabase import getRankingsFromDatabase
from CheckAndPostForSeriesSubmissions import checkNewSubmissions

# Refreshes all other scripts every couple of minutes
def refreshScripts():

    while True:
        checkNewSubmissions()
        timeToSleep = 600
        print("Sleeping for " + str(timeToSleep / 60) + " minutes.")
        sleep(timeToSleep)



if __name__ == '__main__':
    refreshScripts()