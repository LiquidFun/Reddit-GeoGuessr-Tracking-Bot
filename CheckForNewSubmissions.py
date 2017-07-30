import praw
import re
from datetime import datetime
from AddScoresToDatabase import addToDatabase
from AddScoresToDatabase import getTitle
from InitDatabase import getRedditInstance
#import datetime
import operator

import sqlite3

# Checks about 100 new submissions, adds them to the local database, looks for !TrackThisSeries posts
def checkNewSubmissions():

    # Measure time
    startTime = datetime.now()

    # Get reddit instance
    reddit = getRedditInstance()

    subreddit = reddit.subreddit("geoguessr")

    submissionList = subreddit.new(limit = 10)

    addToDatabase(submissionList)

    # Print how long it took
    print(datetime.now() - startTime)


if __name__ == '__main__':
    checkNewSubmissions()