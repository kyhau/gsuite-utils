from __future__ import print_function
import datetime
import httplib2
import sys
from apiclient import discovery
from gsuite_utils.credentials import get_credentials

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gsuite_utilities_gcalendar.json
LOCAL_CREDENTIAL_FILE = 'gsuite_utilities_gcalendar.json'
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret_gsuite_utilities.json'
APPLICATION_NAME = 'G Suite Utilities'


def gcalendar_service():
    """
    Creates a Google Calendar API service object
    :return: a Google Calendar API service object
    """
    credentials = get_credentials(
        LOCAL_CREDENTIAL_FILE,
        CLIENT_SECRET_FILE,
        SCOPES,
        APPLICATION_NAME
    )
    http = credentials.authorize(httplib2.Http())
    return discovery.build('calendar', 'v3', http=http)


def gcalendar_events(service):
    """
    Outputs a list of the next 10 events on the user's calendar.
    :param service: a Google Calendar API service object
    :return: a list
    """
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=20,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    return eventsResult.get('items', [])


def main():
    service = gcalendar_service()

    events = gcalendar_events(service)

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        print(start, end, event['summary'], event['status'])

if __name__ == '__main__':
    sys.exit(main())
