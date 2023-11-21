from __future__ import print_function
import os
import pickle

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_httplib2 import AuthorizedHttp
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

import sqlite3

from .AddScoresToDatabase import convertTitle

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), 'client_secret.json')
APPLICATION_NAME = 'GeoGuessr Tracker Bot'

def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid or expired,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds

def overwriteSeriesTitles():
    """
    Link to sheet:
    https://docs.google.com/spreadsheets/d/1BTO3TI6GxiJmDvMqmafSk5UQs8YDvAafIAv0-h16MOw/edit?usp=sharing
    """
    # Get credentials to be able to access the google sheets API

    print("Opening spreadsheet to get overwrites.")

    # credentials = get_credentials()
    # http = credentials.authorize(httplib2.Http())
    creds = get_credentials()
    http = AuthorizedHttp(creds)
    service = build('sheets', 'v4', http=http, cache_discovery=False)
    # discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
    #                 'version=v4')
    # service = discovery.build('sheets', 'v4', http=http,
    #                           discoveryServiceUrl=discoveryUrl)

    # Set basic info about the spreadsheet
    SHEET_ID = '16VxHWb7TwO4mICr42LIP8RuWRsr-rFD2040hUqdb_yY'
    RANGE_NAME = 'Overwrites!B2:C'
    
    # Get results from spreadsheet    
    result = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    # Connect to database
    database = sqlite3.connect(os.path.join(os.path.dirname(__file__), "database.db"))
    cursor = database.cursor()

    # Update and print series found in spreadsheet
    for row in values:
        try:
            #print('%s, %s -> %s' % (row[0], row[1], convertTitle(row[1])))
            if convertTitle(row[1]) != '':
                if cursor.execute("SELECT COUNT(*) FROM ChallengeRankings WHERE SubmissionID = ?", [row[0]]).fetchone()[0] == 1:
                    #print("Updating records")
                    cursor.execute("UPDATE ChallengeRankings SET SeriesTitle = ? WHERE SubmissionID = ?", [convertTitle(row[1]), row[0]])
        except IndexError:
            pass

    database.commit()
    database.close()

def overwriteBlacklistedUsers():
    """
    Link to sheet:
    https://docs.google.com/spreadsheets/d/1KAPNJKmc5o5pbCs1cmjymLRMHPAyb2_uX0Dqbcf2sUw/edit?usp=sharing
    """

    print("Opening spreadsheet to get blacklisted users.")

    creds = get_credentials()
    http = AuthorizedHttp(creds)
    service = build('sheets', 'v4', http=http, cache_discovery=False)


    # Set basic info about the spreadsheet
    SHEET_ID = '1KAPNJKmc5o5pbCs1cmjymLRMHPAyb2_uX0Dqbcf2sUw'
    RANGE_NAME = 'Blacklist!A2:A'

    # Get results from spreadsheet    
    result = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    print(values)

    # Connect to database
    database = sqlite3.connect(os.path.join(os.path.dirname(__file__), "database.db"))
    cursor = database.cursor()

    cursor.execute("DROP TABLE IF EXISTS BlacklistedUsers")
    cursor.execute("CREATE TABLE BlacklistedUsers (Username PRIMARY KEY)")
    for row in values:
        try:
            username = row[0]
            print('Adding blacklisted user "' + username + '"')
            cursor.execute("INSERT OR REPLACE INTO BlacklistedUsers VALUES (?)", [username])
        except IndexError:
            pass

    database.commit()
    database.close()


if __name__ == '__main__':
    overwriteBlacklistedUsers()
