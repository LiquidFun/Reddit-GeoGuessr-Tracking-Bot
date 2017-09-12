import praw
import re
from datetime import datetime
import operator

import sys, os

import sqlite3

def getDate(submission):
    time = datetime.fromtimestamp(submission.created)
    # return datetime.date.fromtimestamp(time)
    return time.strftime('%Y-%m-%d %H:%M:%S')

def getTitle(submission):
    return convertTitle(submission.title)

def convertTitle(Title):
    delimChars = ['-', ':', '=', '#']

    # Remove parenthesis and square brackets and stuff within them from title
    title = re.sub(r'\([^)]*\)', '', str(Title))
    title = re.sub(r'\[[^]]*\]', '', title)

    # Get first part of title by spliting before line or colon
    for delimChar in delimChars:
        title = title.split(delimChar)[0]

    # Join the resulting chars
    return str(''.join(re.findall('[a-zA-Z]', title)).lower())

# Iterate over the submission list, add submissions to the local database, extract comments, order them by ranking gotten, look for tracking requests and reply to them
def addToDatabase(submissionList):

    # Measure time
    startTime = datetime.now()

    database = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
    cursor = database.cursor()

    #reddit = getRedditInstance()

    botUsername = getBotUsername()

    # Get top level comments from submissions and get their first numbers with regex
    for submission in reversed(list(submissionList)):
        scoresInChallenge = [[-1, ''], [-2, ''], [-3, ''], [-4, '']] 
        for topLevelComment in submission.comments:

            # Looks for !TrackThisSeries and !StopTracking posts and replies to them
            try:
                if topLevelComment.author.name == submission.author.name:
                    alreadyReplied = False
                    if '!trackthisseries' in topLevelComment.body.lower():
                        print("Found track request: " + str(submission.id))

                        # Write new entries to the local database
                        if getTitle(submission) != '':
                            cursor.execute("INSERT OR REPLACE INTO SeriesTracking VALUES (?, ?)", [getTitle(submission), getDate(submission)])
                        
                        for reply in topLevelComment.replies:
                            if reply.author.name == botUsername:
                                alreadyReplied = True

                        if not alreadyReplied:
                            replyToTrackRequest(topLevelComment, True)
                    if '!stoptracking' in topLevelComment.body.lower():
                        print("Found stop tracking request: " + str(submission.id))

                        # Delete old entries in the database
                        if getTitle(submission) != '':
                            cursor.execute("DELETE FROM SeriesTracking WHERE SeriesTitle = ?", [getTitle(submission)])
                        
                        for reply in topLevelComment.replies:
                            if reply.author.name == botUsername:
                                alreadyReplied = True

                        if not alreadyReplied:
                            replyToTrackRequest(topLevelComment, False)
            except AttributeError:
                pass

            doesNotHave = ['previous win:', 'for winning', 'for tying', 'congrats to', '|', 'yesterday\'s winner', "leaderboard:"]

            body = ""
            if topLevelComment is not None:
                body = topLevelComment.body.lower()

            # Avoid comments which do not post their own score; Get the highest number in each comment and add it to the list with the user's username
            if all(string not in body for string in doesNotHave) and topLevelComment is not None and topLevelComment.author is not None:
                try:
                    number = max([int(number.replace(',', '')) for number in re.findall('(?<!round )(?<!~~)(?<!\w)\d+\,?\d+', topLevelComment.body)])
                except (IndexError, ValueError) as e:
                    number = -1
                    pass
                if 0 <= number <= 32395:
                    scoresInChallenge.append([int(number), topLevelComment.author.name])
        scoresInChallenge.sort(key = operator.itemgetter(0), reverse = True)

        # If two players have the same score add the second one to the authors of the first challenge with a pipe character inbetween
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

        # Write new entries to the local database
        #if getTitle(submission) != '':
        record = (str(submission.id), getTitle(submission), str(submission.title), str(scoresInChallenge[0][1]), str(scoresInChallenge[1][1]), str(scoresInChallenge[2][1]), getDate(submission))
        cursor.execute("INSERT OR REPLACE INTO ChallengeRankings VALUES (?, ?, ?, ?, ?, ?, ?)", record)

        #if cursor.execute("SELECT COUNT(*) FROM ChallengeRankings WHERE SubmissionID = '" + submission.id + "'").fetchone()[0] == 0:
        #    cursor.execute("INSERT INTO ChallengeRankings VALUES (?, ?, ?, ?, ?, ?)", record)
        # Update existing entries in the local database
        #else:
        #    cursor.execute("UPDATE ChallengeRankings SET Place1 = '" + str(scoresInChallenge[0][1]) + "', Place2 = '" + str(scoresInChallenge[1][1]) + "', Place3 = '" + str(scoresInChallenge[2][1]) + "' WHERE SubmissionID = '" + str(submission.id) + "'")

    database.commit()
    database.close()

# Reply to the comment which asks the bot to track the series
def replyToTrackRequest(comment, positive):
    if positive == True:
        print("I will be tracking this series: " + getTitle(comment.submission) + " because of this comment " + comment.fullname)
        comment.reply("""I will be tracking this series from now on. """ + getInfoLine())
    else:
        print("I will stop tracking this series: " + getTitle(comment.submission) + " because of this comment " + comment.fullname)
        comment.reply("""I will stop tracking this series from now on. """ + getInfoLine())

# Get the username of the bot which is currently logged in
def getBotUsername():
    inputFile = open(os.path.join(os.path.dirname(__file__), "RedditAPIAccess.txt"))
    lines = []
    for line in inputFile:
        lines.append(line)
    return lines[2].strip()

# Count the number of games in a series up until that post
def getGameCountInSeriesSoFar(submission, includeSubmission):
    database = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
    cursor = database.cursor()
    sign = '<'
    if includeSubmission:
        sign = '<='
    return cursor.execute("SELECT COUNT(*) FROM ChallengeRankings WHERE SeriesTitle = ? AND Date " + sign + " ?", [getTitle(submission), getSubmissionDateFromDatabase(submission)]).fetchone()[0]
    database.close()

# Get the date when the series was added to the database
def getSeriesDateFromDatabase(submission):
    database = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
    cursor = database.cursor()
    return cursor.execute("SELECT StartDate FROM SeriesTracking WHERE SeriesTitle = ?", [getTitle(submission)]).fetchone()[0]
    database.close()

# Get the date in the database for the submission (getDate(submission) and the date in the submission are different for whatever reason so this comparison is more acurate)
def getSubmissionDateFromDatabase(submission):
    database = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
    cursor = database.cursor()
    return cursor.execute("SELECT Date FROM ChallengeRankings WHERE SubmissionID = ?", [str(submission.id)]).fetchone()[0]
    database.close()

def getTotalGameCount():
    database = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
    cursor = database.cursor()
    return cursor.execute("SELECT COUNT(*) FROM ChallengeRankings").fetchone()[0]
    database.close()

def getTotalSeriesCount():
    database = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
    cursor = database.cursor()
    return cursor.execute("SELECT COUNT(*) FROM SeriesTracking").fetchone()[0]
    database.close()

def getSeriesEntries():
    database = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
    cursor = database.cursor()
    return cursor.execute("SELECT * FROM SeriesTracking")
    database.close()

def getInfoLine():
    return """

---

^(I'm a bot, message the author: /u/LiquidProgrammer if I made a mistake.) ^[Usage](https://www.reddit.com/r/geoguessr/comments/6qwn2m/introducing_the_geoguessr_series_tracking_bot/)."""

#if __name__ == '__main__':
    #print(getTitle("[2] (late) Daily Challenge - July 22 (3 min timer)"))