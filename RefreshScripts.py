import plotly.plotly as py
import plotly.graph_objs as go
#import plotly.offline as offline
from CreateTableFromDatabase import getRankingsFromDatabase
from CheckForNewSubmissions import checkNewSubmissions

def refreshScripts():

    checkNewSubmissions()
    sleep(300)



if __name__ == '__main__':
    refreshScripts()