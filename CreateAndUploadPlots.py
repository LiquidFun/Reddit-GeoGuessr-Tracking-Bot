import plotly.plotly as py
import plotly.graph_objs as go
import plotly.offline as offline

import sys, os

from .CreateTableFromDatabase import getRankingsFromDatabase

# Using the plotly API creates a few plots
def createAndUploadPlots(table, plotName):

    # Read plotly username and API key from file (to avoid accidentally publishing it)
    inputFile = open(os.path.join(os.path.dirname(__file__), "PlotlyAPIAccess.txt"))
    lines = []
    for line in inputFile:
        lines.append(line)
    username = lines[0]
    APIkey = lines[1]

    # Sign in plotly
    py.sign_in(username.replace('\n', ''), APIkey.replace('\n', ''))

    #print(table)
    
    # Create the three place bars
    place1 = go.Bar(
        x=[row[0] for row in table],
        y=[row[1] for row in table],
        name='First Place Count',
        marker=dict(color='rgb(252,223,7)')
    )
    place2 = go.Bar(
        x=[row[0] for row in table],
        y=[row[2] for row in table],
        name='Second Place Count',
        marker=dict(color='rgb(204,204,204)')
    )

    place3 = go.Bar(
        x=[row[0] for row in table],
        y=[row[3] for row in table],
        name='Third Place Count',
        marker=dict(color='rgb(142,75,17)')
    )


    data = [place1, place2, place3]
    layout = go.Layout(
        title='%s' % (plotName),
        barmode='group'
    )


    fig = go.Figure(data=data, layout=layout)
    #py.image.save_as(fig, filename='plot.png')
    offline.plot(fig, image = 'png', filename = 'plot.html')
    return py.plot(fig, filename = plotName + '.png', auto_open=False)


if __name__ == '__main__':
    print(createAndUplaodPlots(getRankingsFromDatabase("statelands"), "statelands"))