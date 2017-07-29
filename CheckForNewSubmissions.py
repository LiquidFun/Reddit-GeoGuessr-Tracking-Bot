import praw
import re
from datetime import datetime
from AddScoresToDatabase import addToDatabase
from AddScoresToDatabase import getTitle
from InitDatabase import getRedditInstance
#import datetime
import operator

import sqlite3

def checkNewSubmissions():

    # Measure time
    startTime = datetime.now()

    # Get reddit instance
    reddit = getRedditInstance()

    subreddit = reddit.subreddit("geoguessr")

    #submissionList = [submission for submission in subreddit.submissions() if ('[1' in submission.title or '[2' in submission.title or '[3' in submission.title or '[4' in submission.title or '[5' in submission.title) ]
    submissionList = subreddit.new(limit = 100)

    #database = sqlite3.connect('database.db')
    #cursor = database.cursor()

    addToDatabase(submissionList)

    # Print how long it took
    print(datetime.now() - startTime)


if __name__ == '__main__':
    checkNewSubmissions()