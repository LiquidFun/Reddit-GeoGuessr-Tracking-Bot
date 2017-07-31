#from CreateTableFromDatabase import getRankingsFromDatabase
from CheckForNewSubmissions import checkNewSubmissions

# Refreshes all other scripts every couple of minutes
def refreshScripts():

    checkNewSubmissions()
    sleep(300)



if __name__ == '__main__':
    refreshScripts()