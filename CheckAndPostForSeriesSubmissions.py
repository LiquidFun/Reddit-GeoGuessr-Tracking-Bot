import praw
import re

import sys, os
from datetime import datetime
# from .CreateAndUploadPlots import createAndUploadPlots
from .CreateTableFromDatabase import getRankingsFromDatabase
from .CreateTableFromDatabase import getTableOfSeriesGamesFromDatabase
from .AddScoresToDatabase import getTitle
from .AddScoresToDatabase import getDate
from .AddScoresToDatabase import addToDatabase
from .AddScoresToDatabase import getBotUsername
from .AddScoresToDatabase import getSeriesDateFromDatabase
from .AddScoresToDatabase import getSubmissionDateFromDatabase
from .AddScoresToDatabase import getGameCountInSeriesSoFar
from .AddScoresToDatabase import getInfoLine
from .AddScoresToDatabase import getTotalGameCount
from .AddScoresToDatabase import getTotalSeriesCount
from .AddScoresToDatabase import getSeriesEntries
from .SpreadsheetSeriesAssignment import overwriteSeriesTitles
from .SpreadsheetSeriesAssignment import overwriteBlacklistedUsers
from .InitDatabase import getRedditInstance
from .PasteToPastebin import pasteToPastebin
#import datetime
import operator

import sqlite3

def getFancyTitle(submission):
    delimChars = ['-', ':', '=', '#', '(', ')']

    title = re.sub(r'\([^)]*\)', '', str(submission.title))

    # Get first part of title by spliting before line or colon
    for delimChar in delimChars:
        title = title.split(delimChar)[0]

    # Join the resulting chars
    return title

def getNumberFromTitle(submission):
    title = str(submission.title)

    num = re.search("#\d*", title + "#0")

    return num.group(0)


# Checks about 100 new submissions, adds them to the local database, renews track requests
def checkNewSubmissions():

    # Measure time
    startTime = datetime.now()

    print(str(datetime.now()) + ": Running script.")

    #cursor.execute("INSERT OR REPLACE INTO SeriesTracking VALUES (SeriesTitle = 'redditgeoguessrcommunitychallenge', StartDate = '2017-07-10 01:00:00')")
    #database = sqlite3.connect('database.db')
    #cursor = database.cursor()
    #for val in cursor.execute("SELECT * FROM SeriesTracking"):
    #    print(val)
    #database.close()

    #cursor.commit()

    reddit = getRedditInstance()
    subreddit = reddit.subreddit("geoguessr")

    print(str(datetime.now() - startTime) + ": Acquiring submission list. ")

    # This line is required for some reason
    submissionList = subreddit.new(limit = 1000)

    print(str(datetime.now() - startTime) + ": Overwriting the table of blacklisted users.")    
    overwriteBlacklistedUsers()

    print(str(datetime.now() - startTime) + ": Adding new submissions to the database. ")    
    addToDatabase(submissionList)

    print(str(datetime.now() - startTime) + ": Overwriting the SeriesTitle of posts found in the google sheet. ")    
    overwriteSeriesTitles()

    print(str(datetime.now() - startTime) + ": Checking for new posts which have tracking enabled. ")    
    # This line is required for some reason II
    submissionList = subreddit.new(limit = 1000)

    checkForSeriesSubmissions(submissionList)

    print("Found %s games in total: " % [getTotalGameCount()])

    print("Found %s series in total: " % [getTotalSeriesCount()])
    for series in getSeriesEntries():
        print(series)
            
    # Print how long it took
    print(str(datetime.now() - startTime) + ": Finished. ")    
    print(datetime.now())

# Check the submissionList for submissions for posts whose series is on the tracking list
def checkForSeriesSubmissions(submissionList):
    database = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
    cursor = database.cursor()

    botUsername = getBotUsername()

    #print(botUsername)

    # For each submission check if it's title is in the series tracking list. Then check if the bot has already replied to that post
    for submission in submissionList:
        submission.comments.replace_more(limit=0)
        if cursor.execute("SELECT COUNT(*) FROM SeriesTracking WHERE SeriesTitle = ?", [getTitle(submission)]).fetchone()[0] != 0:
            if getGameCountInSeriesSoFar(submission, True) > 1:
                alreadyPosted = False
                for reply in submission.comments:
                    try:
                        #print(reply.author.name)
                        if reply.author.name == botUsername:
                            alreadyPosted = True
                    except AttributeError:
                        pass
                if not alreadyPosted and getSeriesDateFromDatabase(submission) <= getSubmissionDateFromDatabase(submission):
                    print("Replying to submission: " + str(submission.id) + " in series: " + str(getTitle(submission)))
                    replyTrackedStats(submission)

                    # Was necessary to break because when the bot was a new account it could only post every 10 minutes
                    # break

    #reddit = getRedditInstance()
    #replyTrackedStats(reddit.submission(id = '6qhald'))

    database.close()

# Reply to a post which has tracking enabled with the statistics of the series up until that post excluding itself
def replyTrackedStats(submission, onlyConsoleOutput = False):

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

    #plotlyUrl = createAndUploadPlots(table, "%s %s" % (getFancyTitle(submission), getNumberFromTitle(submission)))

    gameCount = getGameCountInSeriesSoFar(submission, False)


    pastebinText = ""
    for row in getTableOfSeriesGamesFromDatabase(getTitle(submission)):
        for val in row:
            pastebinText += val + ', '
            #print(val)
        pastebinText += '\n'

    #print(pastebinText)

    # Create a paste with a list with all submissions in that series
    pastebinLink = pasteToPastebin("Challenges in series " + getTitle(submission), pastebinText)

    #pastebinLink = ""

    commentText = ("""I have found [%s](%s) challenges in this series so far (excluding the current one):

Ranking|User|1st|2nd|3rd
:--|:--|:--|:--|:--
%s 

Please post your entire score as a top-level reddit comment to have it counted (i.e. if you do a thorough explanation for each round still write your full score somewhere in your comment) %s""" % (gameCount, str(pastebinLink)[2:len(str(pastebinLink)) - 1], text, getInfoLine()))

    if not onlyConsoleOutput:
        submission.reply(commentText)
    print(commentText)

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

    database.close()

if __name__ == '__main__':
    #checkNewSubmissions()
    #reddit = getRedditInstance()
    replyTrackedStats(getRedditInstance().submission(id = '6qoini'))
