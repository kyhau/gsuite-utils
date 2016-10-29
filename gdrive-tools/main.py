from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/admin-reports_v1-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/admin.reports.audit.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'GDrive Tools'


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
    credential_path = os.path.join(credential_dir, 'admin-reports_v1-python-quickstart.json')

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


def gdrive_activities(service, max_results):

    # See Google Apps Admin SDK > Reports API > Activities: list
    # https://developers.google.com/admin-sdk/reports/v1/reference/activities/list

    print('Getting the last {} events'.format(max_results))

    results = service.activities().list(
        applicationName='drive',
        userKey='all',
        maxResults=max_results
    ).execute()

    activities = results.get('items', [])

    for activity in activities:

        # The complete list of drive event names can be found here
        # https://developers.google.com/admin-sdk/reports/v1/reference/activity-ref-appendix-a/drive-event-names

        gdrive_event_params = activity['events'][0]['parameters']
        ret = {}
        for i in gdrive_event_params:
            if 'value' in i.keys():
                ret[i['name']] = i['value']
            elif 'intValue' in i.keys():
                ret[i['name']] = i['intValue']
            elif 'boolValue' in i.keys():
                ret[i['name']] = i['boolValue']

        print('--------------------------------------------------------')
        print('time     : {}'.format(activity['id']['time']))
        print('actor    : {}'.format(activity['actor']['email']))
        print('event    : {}'.format(activity['events'][0]['name']))
        print('doc_title: {}'.format(ret['doc_title']))
        print('doc_type : {}'.format(ret['doc_type']))
        print('doc_id   : {}'.format(ret['doc_id']))
        print('owner    : {}'.format(ret['owner']))
        print('primary_event: {}'.format(ret['primary_event']))


def main():
    # Creates a Google Admin SDK Reports API service object
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('admin', 'reports_v1', http=http)

    gdrive_activities(service, max_results=10)


if __name__ == '__main__':
    main()
