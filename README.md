# Using it for tracking

Read [here](https://www.reddit.com/r/geoguessr/comments/6qwn2m/introducing_the_geoguessr_series_tracking_bot/) for information how to use it in the sub and the less technical stuff (feel free to message me on reddit if you have questions).

# Running the bot

## Dependancies

SQLite3, PRAW, Plotly, Google Sheets API

## Files

### InitDatabase.py

Run this file to initialize and generate the local copy of the database ("database.db"). It gets all submissions from reddit and extracts the scores in each comment. It then selects the 3 people with the best scores and puts only their names in the database. It also checks for any !TrackThisSeris and !StopTracking posts and adds them to the SeriesTracking table, and also replies to these requests. It doesn't write the replies for the tracking itself.

This file should be run once when downloaded. 

`python3 InitDatabase.py`

### CheckAndPostForSeriesSubmissions.py

This file adds recent submissions to the already initialized database, may overwrite some because of new comments. After that it checks a spreadsheet for manual overwrites of certain submissions with overwrites for the SeriesTitle attribute in the database. Then it checks if there are any new submissions which have tracking enabled and replies to them with statistics for that series. It can quit if it replies once because of the 10 minute posting limitation for new accounts.

This file should be run if you want to do one check and not more. 

`python3 CheckAndPostForSeriesSubmissions.py`

### RefreshScripts.py

This file runs the before mentioned script every couple of minutes.

This file should be run once on every startup as it continually looks for new submissions. 

`python3 RefreshScripts.py`. 

---

All other files are for internal use and usually don't need running. In case you want to understand them you can look at the comments in the files themselves.

## API files

### RedditAPIAccess.txt

1. client_id
2. client_secret
3. Reddit Username
4. Reddit Password

### PlotlyAPIAccess.txt

1. Username
2. API key

### PastebinAPIAccess.txt

1. API dev key
