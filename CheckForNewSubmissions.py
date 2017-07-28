import praw
import re
from datetime import datetime
#import datetime
import operator

import sqlite3

def getDate(submission):
    time = datetime.fromtimestamp(submission.created)
    # return datetime.date.fromtimestamp(time)
    return time.strftime('%Y-%m-%d')

def getTitle(title):
    delimChars = ['-', ':', '=', '#', '(', ')']

    # Get first part of title by spliting before line or colon
    for delimChar in delimChars:
        title = title.split(delimChar)[0]

    # Join the resulting chars
    return ''.join(re.findall('[a-zA-Z]', title)).lower()

def checkNewSubmissions():

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

    #print(username)

    # Get reddit instance
    reddit = praw.Reddit(client_id=client_id.replace('\n', ''), 
                         client_secret=client_secret.replace('\n', ''), 
                         user_agent='linux:geoguessr_bot:0.1 (by /u/LiquidProgrammer',
                         username=username.replace('\n', ''),
                         password=password.replace('\n', ''))

    subreddit = reddit.subreddit("geoguessr")

    #submissionList = [submission for submission in subreddit.submissions() if ('[1' in submission.title or '[2' in submission.title or '[3' in submission.title or '[4' in submission.title or '[5' in submission.title) ]
    submissionList = subreddit.new(limit = 50)

    database = sqlite3.connect('database.db')
    cursor = database.cursor()

    for row in cursor.execute("SELECT COUNT(*) FROM ChallengeRankings WHERE SubmissionID = '6p944h'"):
        print(row[0])


    """
    trackedSeriesNames = set()

    #Add the titles from the last 
    inputFile = open("Series.txt")
    for line in inputFile:
        trackedSeriesNames.add(line.replace('\n', ''))
    inputFile.close()

    # Get top level comments from submissions and get their first numbers with regular expressions
    for index, submission in enumerate(submissionList):
        scoresInChallenge = [[-1, ''], [-2, ''], [-3, '']] 
        for topLevelComment in submission.comments:
            if topLevelComment.author == submission.author:
                if '!trackthisseries' in topLevelComment.body.lower():
                    trackedSeriesNames.add(getTitle(submission.title))
            if 'Previous win:' not in topLevelComment.body and 'for winning yesterday' not in topLevelComment.body and '|' not in topLevelComment.body and topLevelComment is not None and topLevelComment.author is not None:
                try:
                    number = max([int(number.replace(',', '')) for number in re.findall('(?<!round )(?<!~~)(?<!\w)\d+\,?\d+', topLevelComment.body)])
                except (IndexError, ValueError) as e:
                    number = -1
                    break
                if 0 <= number <= 32395:
                    scoresInChallenge.append([int(number), topLevelComment.author])
        scoresInChallenge.sort(key = operator.itemgetter(0), reverse = True)

        # If two players have the same score add them to the authors of the first challenge with a pipe character inbetween
        for i in range(0, 3):
            while scoresInChallenge[i][0] == scoresInChallenge[i + 1][0]:
                scoresInChallenge[i][1] += "|" + scoresInChallenge[i + 1][1]
                del scoresInChallenge[i + 1]
        #print(index)
        #print(getTitle(submission.title))
        #print(submission.id)
        #print(scoresInChallenge[0][1])
        #print(scoresInChallenge[1][1])
        #print(scoresInChallenge[2][1])
        #print(submission.created)
        record = (getTitle(submission.title), str(submission.id), str(scoresInChallenge[0][1]), str(scoresInChallenge[1][1]), str(scoresInChallenge[2][1]), getDate(submission))
        cursor.execute("INSERT INTO ChallengeRankings VALUES (?, ?, ?, ?, ?, ?)", record)

    # Write SeriesTitles to file
    inputFile = open("Series.txt", 'w+')
    for series in trackedSeriesNames:
        print(series, file = inputFile)
    inputFile.close()

    for title in trackedSeriesNames:
        print(title)

    # Commit the changes to the database
    database.commit()
    database.close()

    """

    # Print how long it took
    print(datetime.now() - startTime)


if __name__ == '__main__':
    checkNewSubmissions()