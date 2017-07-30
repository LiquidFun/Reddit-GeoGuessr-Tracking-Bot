import praw
import re
from datetime import datetime
from AddScoresToDatabase import addToDatabase
#import datetime
import operator

import sqlite3

def getRedditInstance():
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

    return reddit

def runScript():

    # Measure time
    startTime = datetime.now()

    print(str(datetime.now() - startTime) + ": Getting reddit instance. ")

    reddit = getRedditInstance()

    print(str(datetime.now() - startTime) + ": Logged in as " + str(reddit.user.me()) + ". ")

    subreddit = reddit.subreddit("geoguessr")

    print(str(datetime.now() - startTime) + ": Creating submission list. ")

    # Get submissions from the subreddit
    submissionList = [submission for submission in subreddit.submissions() if ('[1' in submission.title or '[2' in submission.title or '[3' in submission.title or '[4' in submission.title or '[5' in submission.title) ]
    #submissionList = subreddit.new(limit = 50)

    print(str(datetime.now() - startTime) + ": Opening SQL Database. ")

    database = sqlite3.connect('database.db')
    cursor = database.cursor()

    print(str(datetime.now() - startTime) + ": Creating the SQL table. ")

    cursor.execute("DROP TABLE ChallengeRankings")
    cursor.execute("CREATE TABLE ChallengeRankings (SubmissionID text, SeriesTitle text, Place1 text, Place2 text, Place3 text, Date timestamp)")

    cursor.execute("DROP TABLE SeriesTracking")
    cursor.execute("CREATE TABLE SeriesTracking (SeriesTitle text, StartDate timestamp)")


    #cursor.execute("DROP TABLE TrackingRequests")
    #cursor.execute("CREATE TABLE TrackingRequests (CommentID text)")

    #cursor.execute("CREATE TABLE SeriesStopTracking (SeriesTitle text)")

    # Commit the changes to the database
    database.commit()
    database.close()

    print(str(datetime.now() - startTime) + ": Adding data to database. ")

    addToDatabase(submissionList)

    print(str(datetime.now() - startTime) + ": Added " + cursor.execute("SELECT COUNT(*) FROM ChallengeRankings") + " challenges.")
    print(str(datetime.now() - startTime) + ": Added " + cursor.execute("SELECT COUNT(*) FROM SeriesTracking") + " series:")
    print(cursor.execute("SELECT * FROM SeriesTracking"))
    #for title in trackedSeriesNames:
    #    print(title)

    # Print how long it took
    print(datetime.now() - startTime)


if __name__ == '__main__':
    runScript()