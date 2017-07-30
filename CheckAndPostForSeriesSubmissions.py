import praw
import re
from datetime import datetime
from CreateAndUploadPlots import createAndUploadPlots
from CreateTableFromDatabase import getRankingsFromDatabase
from AddScoresToDatabase import getTitle
from AddScoresToDatabase import getDate
from InitDatabase import getRedditInstance
#import datetime
import operator

import sqlite3

# Check the last ~100 submissions for posts which are on the tracking list
def checkForSeriesSubmissions():

    # Measure time
    startTime = datetime.now()

    # Get reddit instance
    reddit = getRedditInstance()

    submission = reddit.submission(id='6qaxro')
    replyTrackedStats(submission)

# Reply to a post which has tracking enabled with the statistics of the series up until that post excluding itself
def replyTrackedStats(submission):

    table = getRankingsFromDatabase(submission)
    text = ""
    place = 0
    for index, row in enumerate(table):
        #print(row)
        if index != 0:
            if table[index][1] != table[index - 1][1] or table[index][2] != table[index - 1][2] or table[index][3] != table[index - 1][3]:
                place = index

        text += str(place + 1) + getPostFix(place + 1)
        for i, val in enumerate(row):
            if i == 0:
                text += '|/u/' + str(val)
            else:
                text += '|' + str(val)
        text += '\n'

    url = createAndUploadPlots(table, submission.id)

    gameCount = getGameCountInSeriesSoFar(submission)

    #submission.reply
    print("I have found " + str(gameCount) + " challenges in this series so far:\n\nRanking|User|1st|2nd|3rd\n:--|:--|:--|:--|:--\n" + 
        text + "\n\n[Here](" + 
        url + ") is a visualization of the current stats.\n\n---\n\n^(I'm a bot, message the author: /u/LiquidProgrammer if I made a mistake.) ^[Usage](https://www.reddit.com/r/geoguessr/comments/6haay2/).")

# Get the postfix st, nd, rd or th for a number
def getPostFix(index):
    if index % 10 == 1 and index % 100 != 11:
        return 'st'
    if index % 10 == 2 and index % 100 != 12:
        return 'nd'
    if index % 10 == 3 and index % 100 != 13:
        return 'rd'
    else:
        return 'th'

# Count the number of games in a series up until that post
def getGameCountInSeriesSoFar(submission):
    database = sqlite3.connect("database.db")
    cursor = database.cursor()

    return cursor.execute("SELECT COUNT(*) FROM ChallengeRankings WHERE SeriesTitle = '" + getTitle(submission) + "' AND Date <= '" + str(getDate(submission)) + "'").fetchone()[0]

    database.close()

if __name__ == '__main__':
    checkForSeriesSubmissions()