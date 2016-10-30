from __future__ import print_function
import httplib2
import sys
from apiclient import discovery
from gsuite_utils.credentials import get_credentials

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gsuite_utilities_gdrive.json
LOCAL_CREDENTIAL_FILE = 'gsuite_utilities_gdrive.json'
SCOPES = 'https://www.googleapis.com/auth/admin.reports.audit.readonly'
CLIENT_SECRET_FILE = 'client_secret_gsuite_utilities.json'
APPLICATION_NAME = 'G Suite Utilities'


def gdrive_service():
    """
    Creates a Google Admin SDK Reports API service object
    :return: a Google Admin SDK Reports API service object
    """
    credentials = get_credentials(
        LOCAL_CREDENTIAL_FILE,
        CLIENT_SECRET_FILE,
        SCOPES,
        APPLICATION_NAME
    )
    http = credentials.authorize(httplib2.Http())
    return discovery.build('admin', 'reports_v1', http=http)


def gdrive_activities(service, max_results):
    """
    Outputs a list of the last 'max_results' google drive evetns.
    :param service: a Google Admin SDK Reports API service object
    :param max_results:
    :return: a list
    """

    # See Google Apps Admin SDK > Reports API > Activities: list
    # https://developers.google.com/admin-sdk/reports/v1/reference/activities/list

    print('Getting the last {} events'.format(max_results))

    results = service.activities().list(
        applicationName='drive',
        userKey='all',
        maxResults=max_results
    ).execute()

    return results.get('items', [])


def main():
    service = gdrive_service()

    activities = gdrive_activities(service, max_results=10)

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

if __name__ == '__main__':
    sys.exit(main())
