import praw
import re
from datetime import datetime
from CreateAndUploadPlots import createAndUploadPlots
from CreateTableFromDatabase import getRankingsFromDatabase
from AddScoresToDatabase import getTitle
#import datetime
import operator

import sqlite3

def checkForSeriesSubmissions():

    # Measure time
    startTime = datetime.now()

    # Read reddit client_id and client_secret from file (to avoid accidentally publishing it)
    inputFile = open("RedditAPIAccess.txt")
    lines = []
    for line in inputFile:
        lines.append(line)
    client_id = lines[0]
    client_secret = lines[1]
    username = lines[2]
    password = lines[3]

    # Get reddit instance
    reddit = praw.Reddit(client_id=client_id.replace('\n', ''), 
                         client_secret=client_secret.replace('\n', ''), 
                         user_agent='linux:geoguessr_bot:0.1 (by /u/LiquidProgrammer',
                         username=username.replace('\n', ''),
                         password=password.replace('\n', ''))

    database = sqlite3.connect('database.db')
    cursor = database.cursor()

    submission = reddit.submission(id='6haay2')
    replyTrackedStats(submission)

def replyTrackedStats(submission):

    table = getRankingsFromDatabase("database.db", submission)
    text = ""
    place = 0
    for index, row in enumerate(table):
        #print(row)
        if index != 0:
            if table[index][1] != table[index - 1][1] or table[index][2] != table[index - 1][2] or table[index][3] != table[index - 1][3]:
                place = index

        text += str(place + 1) + getPostFix(place + 1)
        for val in row:
            text += '|' + str(val)
        text += '\n'

    url = createAndUploadPlots(table, submission.id)

    #if 0 = 1:
        #submission.reply
    print("I have found # challenges in this series so far:\n\nRanking|User|1st|2nd|3rd\n:--|:--|:--|:--|:--\n" + text + "\n\n[Here](" + url + ") is a visualization of the current stats.\n\n---\n\n^(I'm a bot, message the author: /u/LiquidProgrammer if I made a mistake.) ^[Usage](https://www.reddit.com/r/geoguessr/comments/6haay2/).")

def getPostFix(index):
    if index % 10 == 1 and index % 100 != 11:
        return 'st'
    if index % 10 == 2 and index % 100 != 12:
        return 'nd'
    if index % 10 == 3 and index % 100 != 13:
        return 'rd'
    else:
        return 'th'


if __name__ == '__main__':
    checkForSeriesSubmissions()