import praw
import re
from datetime import datetime
from .AddScoresToDatabase import addToDatabase
from .AddScoresToDatabase import getTotalGameCount
from .AddScoresToDatabase import getTotalSeriesCount
from .AddScoresToDatabase import getSeriesEntries

import sys, os
#import datetime
import operator

import sqlite3

def getRedditInstance():
    # Read reddit client_id and client_secret from file (to avoid accidentally publishing it)
    inputFile = open(os.path.join(os.path.dirname(__file__), "RedditAPIAccess.txt"))
    lines = []
    for line in inputFile:
        lines.append(line)
    client_id = lines[0]
    client_secret = lines[1]
    username = lines[2]
    password = lines[3]

    # Get reddit instance
    reddit = praw.Reddit(client_id=client_id.rstrip(), 
                         client_secret=client_secret.rstrip(), 
                         user_agent='linux:geoguessr_bot:0.1 (by /u/LiquidProgrammer',
                         username=username.rstrip(),
                         password=password.rstrip())

    return reddit

def runScript():

    # Measure time
    startTime = datetime.now()

    print(str(datetime.now()) + ": Starting script.")

    print(str(datetime.now() - startTime) + ": Getting reddit instance. ")

    # Get reddit instance as GeoGuessrTrackingBot
    reddit = getRedditInstance()

    print(str(datetime.now() - startTime) + ": Logged in as " + str(reddit.user.me()) + ". ")

    for subredditName in ['geoguessr', 'geochallenges']:
        subreddit = reddit.subreddit(subredditName)

        print(str(datetime.now() - startTime) + ": Creating submission list. ")

        # Get all the submissions from the subreddit
        submissionList = [submission for submission in subreddit.submissions() if ('[1' in submission.title or '[2' in submission.title or '[3' in submission.title or '[4' in submission.title or '[5' in submission.title) ]
        #submissionList = subreddit.new(limit = 50)

        print(str(datetime.now() - startTime) + ": Opening SQL Database. ")

        # Open the database
        database = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
        cursor = database.cursor()

        print(str(datetime.now() - startTime) + ": Creating the SQL table. ")

        # Create tables in database
        cursor.execute("DROP TABLE IF EXISTS ChallengeRankings")
        cursor.execute("CREATE TABLE ChallengeRankings (SubmissionID text PRIMARY KEY, SeriesTitle text, SubmissionTitle text, Place1 text, Place2 text, Place3 text, Date timestamp)")

        cursor.execute("DROP TABLE IF EXISTS SeriesTracking")
        cursor.execute("CREATE TABLE SeriesTracking (SeriesTitle text PRIMARY KEY, StartDate timestamp)")

        print(str(datetime.now() - startTime) + ": Adding data to database. ")

        # Add the statistics to the database
        addToDatabase(submissionList)

        print(str(datetime.now() - startTime) + ": Added " + str(getTotalGameCount()) + " challenges.")
        print(str(datetime.now() - startTime) + ": Added " + str(getTotalSeriesCount()) + " series:")
        for series in getSeriesEntries():
            print(series)

        # Commit the changes to the database
        database.commit()
        database.close()

        # Print how long it took
        print(datetime.now() - startTime)


if __name__ == '__main__':
    runScript()
