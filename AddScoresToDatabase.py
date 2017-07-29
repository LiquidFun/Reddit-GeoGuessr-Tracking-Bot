import praw
import re
from datetime import datetime
#import datetime
import operator

import sqlite3

def getDate(submission):
    time = datetime.fromtimestamp(submission.created)
    # return datetime.date.fromtimestamp(time)
    return time.strftime('%Y-%m-%d %H:%M:%S')

def getTitle(submission):
    delimChars = ['-', ':', '=', '#', '(', ')']

    title = submission.title

    # Get first part of title by spliting before line or colon
    for delimChar in delimChars:
        title = title.split(delimChar)[0]

    # Join the resulting chars
    return ''.join(re.findall('[a-zA-Z]', title)).lower()

def addToDatabase(submissionList):

    # Measure time
    startTime = datetime.now()

    database = sqlite3.connect('database.db')
    cursor = database.cursor()

    trackedSeriesNames = set()

    # Add the titles from the last session
    seriesFile = open("Series.txt")
    for line in seriesFile:
        trackedSeriesNames.add(line.replace('\n', ''))
    seriesFile.close()

    trackedSeriesCommentIDs = set()

    # Get the !trackthisseries posts already replied to
    # Add the series IDs which the bot has already replied to
    inputFile = open("trackThisSeriesCommentIDs.txt")
    for line in inputFile:
        trackedSeriesCommentIDs.add(line.replace('\n', ''))
    inputFile.close()

    # Get top level comments from submissions and get their first numbers with regular expressions
    for submission in submissionList:
        scoresInChallenge = [[-1, ''], [-2, ''], [-3, ''], [-4, '']] 
        for topLevelComment in submission.comments:
            try:
                if topLevelComment.author.name == submission.author.name:
                    if '!trackthisseries' in topLevelComment.body.lower():
                        print(submission.id)
                        trackedSeriesNames.add(getTitle(submission))
                        if topLevelComment.fullname not in trackedSeriesCommentIDs:
                            replyToTrackRequest(topLevelComment)
            except AttributeError:
                pass
            if 'Previous win:' not in topLevelComment.body and 'for winning yesterday' not in topLevelComment.body and '|' not in topLevelComment.body and topLevelComment is not None and topLevelComment.author is not None:
                try:
                    number = max([int(number.replace(',', '')) for number in re.findall('(?<!round )(?<!~~)(?<!\w)\d+\,?\d+', topLevelComment.body)])
                except (IndexError, ValueError) as e:
                    number = -1
                    break
                if 0 <= number <= 32395:
                    scoresInChallenge.append([int(number), topLevelComment.author.name])
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

        if cursor.execute("SELECT COUNT(*) FROM ChallengeRankings WHERE SubmissionID = '" + submission.id + "'").fetchone()[0] == 0:
            record = (getTitle(submission), str(submission.id), str(scoresInChallenge[0][1]), str(scoresInChallenge[1][1]), str(scoresInChallenge[2][1]), getDate(submission))
            cursor.execute("INSERT INTO ChallengeRankings VALUES (?, ?, ?, ?, ?, ?)", record)
        else:
            cursor.execute("UPDATE ChallengeRankings SET Place1 = " + str(scoresInChallenge[0][1]) + ", SET Place2 = " + str(scoresInChallenge[1][1]) + ", SET Place3 = " + str(scoresInChallenge[2][1]) + " WHERE SubmissionID = '" + submission.id + "'")

    # Write the !trackthisseries already replied to posts to the file
    inputFile = open("trackThisSeriesCommentIDs.txt", 'w+')
    for commentID in trackedSeriesCommentIDs:
        print(commentID, file = inputFile)
    inputFile.close()

    # Write SeriesTitles to file
    seriesFile = open("Series.txt", 'w+')
    for series in trackedSeriesNames:
        print(series, file = seriesFile)
    seriesFile.close()

    database.commit()
    database.close()

def replyToTrackRequest(comment):
    print("I will be tracking this comment" + comment.fullname)
    #comment.reply("I will be tracking this series from now on.")
