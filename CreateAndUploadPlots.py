import plotly.plotly as py
import plotly.graph_objs as go
#import plotly.offline as offline
from CreateTableFromDatabase import getRankingsFromDatabase

def createAndUplaodPlots(table, plotName):

    #offline.init_notebook_mode()

    # Read reddit client_id and client_secret from file (to avoid accidentally publishing it)
    inputFile = open("PlotlyAPIAccess.txt")
    lines = []
    for line in inputFile:
        lines.append(line)
    username = lines[0]
    password = lines[1]



    py.sign_in(username.replace('\n', ''), password.replace('\n', ''))

    print(table)
    
    place1 = go.Bar(
        x=[row[0] for row in table],
        y=[row[1] for row in table],
        name='First Place',
        marker=dict(color='rgb(252,223,7)')
    )
    place2 = go.Bar(
        x=[row[0] for row in table],
        y=[row[2] for row in table],
        name='Second Place',
        marker=dict(color='rgb(204,204,204)')
    )

    place3 = go.Bar(
        x=[row[0] for row in table],
        y=[row[3] for row in table],
        name='Third Place',
        marker=dict(color='rgb(142,75,17)')
    )


    data = [place1, place2, place3]
    layout = go.Layout(
        barmode='group'
    )


    fig = go.Figure(data=data, layout=layout)
    #py.image.save_as(fig, filename='plot.png')
    url = py.plot(fig, filename = plotName + '.png')
    print(url)
    #offline.plot(fig, filename='grouped-bar', image = 'png')
    #offline.plot(fig, image = 'png', filename = 'plot.html')


if __name__ == '__main__':
    createAndUplaodPlots(getRankingsFromDatabase("database.db", "statelands"), "statelands")