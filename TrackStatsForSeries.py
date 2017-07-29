# from __future__ import print_function
import httplib2
import os
import pprint

import praw
import re
import datetime
from time import gmtime, strftime, localtime

#from apiclient import discovery
#from oauth2client import client
#from oauth2client import tools
#from oauth2client.file import Storage

#try:
#    import argparse
#    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#except ImportError:
#    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
#SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
#CLIENT_SECRET_FILE = 'client_secret.json'
#APPLICATION_NAME = 'GeoGuessr Statistics Tracker'

def getDate(submission):
    time = datetime.fromtimestamp(submission.created)
    # return datetime.date.fromtimestamp(time)
    return time.strftime('%Y-%m-%d %H:%M:%S')
    

def getTitle(title):
    delimChars = ['-', ':', '=', '#', '(', ')']

    # Get first part of title by spliting before line or colon
    for delimChar in delimChars:
        title = title.split(delimChar)[0]

    # Join the resulting chars
    return ''.join(re.findall('[a-zA-Z]', title))


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def enoughGames(scoreList):
    gamesPlayed = 0
    for score in scoreList:
        if isNumber(score):
            gamesPlayed += 1
    if gamesPlayed > 0:
        return True
    else:
        return False

def runScript():
    """
    Link to sheet:
    https://docs.google.com/spreadsheets/d/1BTO3TI6GxiJmDvMqmafSk5UQs8YDvAafIAv0-h16MOw/edit?usp=sharing
    """
    # Get credentials to be able to access the google sheets API

    
    f = open('log.txt', 'a')
    print("Script run at: " + str(strftime("%Y-%m-%d %H:%M:%S", localtime())), file=f)
    print("Script run at: " + str(strftime("%Y-%m-%d %H:%M:%S", localtime())))  
    

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
                         user_agent='linux:geoguessr_bot:0.1 (by /u/LiquidProgrammer')

    # print(client_id)
    # print(client_secret)
    # exit()

    # Get subreddit instance
    subreddit = reddit.subreddit('geoguessr')

    # Generate submission list which shall be used in the rest of the file
    # Necessary so that certain posts could be consistently ignored
    # Rules for ignoring post are described in the overview sheet
    #submissionList = [submission for submission in subreddit.submissions() if ('[1' in submission.title or '[2' in submission.title or '[3' in submission.title or '[4' in submission.title or '[5' in submission.title) ]
    submissionList = [submission for submission in subreddit.new(limit = 10)]

    #subreddit.comments

    #for submission in submissionList:
    #    for topLevelComment in submission.comments:



    # Create a set with all the names
    names = set([comment.author.name for submission in submissionList for comment in submission.comments if comment is not None and comment.author is not None])

    # Generate a date list which contains the date and the post title
    dates = [getTitle(submission.title) for submission in submissionList]
    cornerValue = ''

    dateSet = set()
    for date in dates:
        dateSet.add(date);

    #print(dateSet)

    # Add the the value in the starting cell to the date list
    dates.insert(0, cornerValue)

    # Create a new list, this will be the list we will use to create the data list 
    scores = []

    # Add empty values for every name and every submission
    for name in names:
        scores.append(['' for i in range(0, len(submissionList))])

    # Convert the set to a list so that we could sort it alphabetically
    nameList = list(names)
    nameList.sort(key=str.lower)

    # Insert the names at the start of the score list
    for index, scoreLine in enumerate(scores):
        scoreLine.insert(0, nameList[index])

    # Might be necessary if there is a post which has a lot of comments
    # submission.comments.replace_more(limit=0)

    # Get top level comments from submissions and get their first numbers with regular expressions
    for index, submission in enumerate(submissionList):
        for topLevelComment in submission.comments:
            if 'Previous win:' not in topLevelComment.body and 'for winning yesterday' not in topLevelComment.body and '|' not in topLevelComment.body and topLevelComment is not None and topLevelComment.author is not None:
                try:
                    number = max([int(number.replace(',', '')) for number in re.findall('(?<!round )(?<!~~)(?<!\w)\d+\,?\d+', topLevelComment.body)])
                except (IndexError, ValueError) as e:
                    number = -1
                    break
                if 0 <= number <= 32395:
                    scores[nameList.index(topLevelComment.author.name)][index + 1] = number

    # Read challenge overwrites
    # overwrites = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=RANGE_OVERWRITE_SCORE).execute().get('values', [])

    # Overwrite in scores
    """
    for overwrite in overwrites:
        for index, submission in enumerate(submissionList):
            try:
                if submission.id == overwrite[2]:
                    scores[nameList.index(overwrite[0]) + 1][index + 1] = int(overwrite[1])
            except IndexError:
                pass
    """

    # Remove players who have very few games
    scores[:] = [scoreList for scoreList in scores if enoughGames(scoreList)]
    nameList[:] = [scoreList[0] for scoreList in scores]

    # Insert the dates on the top of the scores 2D list
    scores.insert(0, dates)

    firstPlaces = {name:[0, 0, 0, 0] for name in nameList}

    # Calculate first/second/third places
    for i in range(1, len(scores[0])):
        currScores = [-1, -2, -3]
        for j in range(1, len(scores)):
            try:
                currScores.append(int(scores[j][i]))
            except ValueError:
                pass
        currScores.sort(reverse = True)
        while currScores[0] == currScores[1]:
            del currScores[1]
        while currScores[1] == currScores[2]:
            del currScores[2]
        # print(currScores)
        for place in range(0, 3):
            for j in range(1, len(scores)):
                if scores[j][i] == currScores[place]:
                    firstPlaces[nameList[j - 1]][place] += 1

    # Calculate games played
    for scoreList in scores:
        for score in scoreList:
            try:
                if isNumber(score):
                    firstPlaces[scoreList[0]][3] += 1
            except (IndexError, ValueError) as e:
                pass

    # Create the places things
    places = [[] for i in range(0, len(nameList))]

    for key, value in firstPlaces.items():
        places[nameList.index(key)] = value


    #places = {'values': places[:]}
    # print(places)

    #data = {'values': [scoreList[:] for scoreList in scores]}

    #data_file = open('data.txt', 'w')

    #for row in scores:
    #    for val in row:
    #        print(val, end=', ', file = data_file)
    #    print('\n')

    foile = open('data.txt', 'w')
    print(scores, file = foile)

    for date in dateSet:
        file = open('series/' + date + '.txt', 'w+')
        #for index in range(0, len(scores)):
        #    print(scores[index][0], end = '', file = file)

        for y in range(1, len(scores)):
            for x in range(0, len(scores[y])):
                if scores[0][x] == date or x == 0:
                    print(scores[y][x], end = ', ', file = file)
            print('\n', end = '', file = file)
        file.close()
    # print(data)
    """
    # Write data to sheet
    service.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=RANGE_ENTRY, body=data, valueInputOption='USER_ENTERED').execute()

    # Write places to sheet
    service.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=RANGE_PLACES, body=places, valueInputOption='USER_ENTERED').execute()

    # Update "Last Update" value
    service.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=RANGE_LAST_UPDATE, body={'values': [[strftime("%Y-%m-%d\n%H:%M:%S", localtime())]]}, valueInputOption='USER_ENTERED').execute()    

    # Update "Challenges parsed" value
    service.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=RANGE_CHALLENGES_PARSED, body={'values': [[len(submissionList)]]}, valueInputOption='USER_ENTERED').execute()    
    """
    print('Successfully entered data.', file=f)
    f.close()

if __name__ == '__main__':
    runScript()