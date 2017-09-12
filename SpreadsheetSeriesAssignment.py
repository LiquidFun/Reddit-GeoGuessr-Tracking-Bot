from __future__ import print_function
import httplib2
import sys, os

import re

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import sqlite3

from .AddScoresToDatabase import convertTitle

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), 'client_secret.json')
APPLICATION_NAME = 'GeoGuessr Tracker Bot'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def overwriteSeriesTitles():
    """
    Link to sheet:
    https://docs.google.com/spreadsheets/d/1BTO3TI6GxiJmDvMqmafSk5UQs8YDvAafIAv0-h16MOw/edit?usp=sharing
    """
    # Get credentials to be able to access the google sheets API

    print("Opening spreadsheet to get overwrites.")

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

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
            print('%s, %s -> %s' % (row[0], row[1], convertTitle(row[1])))
            if convertTitle(row[1]) != '':
                if cursor.execute("SELECT COUNT(*) FROM ChallengeRankings WHERE SubmissionID = ?", [row[0]]).fetchone()[0] == 1:
                    #print("Updating records")
                    cursor.execute("UPDATE ChallengeRankings SET SeriesTitle = ? WHERE SubmissionID = ?", [convertTitle(row[1]), row[0]])
        except IndexError:
            pass

    database.commit()
    database.close()


if __name__ == '__main__':
    overwriteSeriesTitles()
