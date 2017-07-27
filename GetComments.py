import praw
import re
from datetime import datetime

def getTitle(title):
    delimChars = ['-', ':', '=', '#', '(', ')']

    # Get first part of title by spliting before line or colon
    for delimChar in delimChars:
        title = title.split(delimChar)[0]

    # Join the resulting chars
    return ''.join(re.findall('[a-zA-Z]', title))

def runScript():

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
    submissionList = subreddit.new(limit = 10)

    #print(reddit.user.me())

    #for comment in subreddit.comments(limit = 10):
    #    print(comment.author)

    #for comment in reddit.subreddit('redditdev').comments(limit=25):
    #    print(comment.author)

    # Delim chars for where to split the title and to get the seriesName
    
    trackedSeriesNames = set()

    #Add the titles from the last 
    inputFile = open("Series.txt")
    for line in inputFile:
        trackedSeriesNames.append(line.replace('\n', ''))

    # Add titles
    for submission in submissionList:
        for topLevelComment in submission.comments:
            if topLevelComment.author == submission.author:
                if re.search('14968', topLevelComment.body.lower()) is not None:
                    trackedSeriesNames.add(getTitle(submission.title))
        #print(submission.title)

    for title in trackedSeriesNames:
        print(title)

    # Print how long it took
    print(datetime.now() - startTime)

if __name__ == '__main__':
    runScript()