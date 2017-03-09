from __future__ import print_function

import httplib2
from apiclient import discovery
from datetime import datetime

from gsuite_tools import (
    EXPECTED_DATETIME_FORMATS,
    TimeEntryData,
    worklog_time_spent
)
from credentials import get_credentials


class GCalendar(object):
    def __init__(self, credentials, client_secret):
        self.credentials = credentials
        self.client_secret = client_secret
        self.gcalender = self.authorize_gcalender()

    def authorize_gcalender(self):
        """
        Creates a Google Calendar API service object
        :return: a Google Calendar API service object
        """
        credentials = get_credentials(
            self.credentials,
            self.client_secret,
            'https://www.googleapis.com/auth/calendar.readonly',
            'G Suite Utilities'
        )
        http = credentials.authorize(httplib2.Http())
        return discovery.build('calendar', 'v3', http=http)

    def gcalendar_events(self, start_date, end_date):
        """
        Outputs a list of the next 'max_results' events on the user's calendar.
        :param service: a Google Calendar API service object
        :return: a list
        """
        min_time = start_date.isoformat() + 'Z' # 'Z' indicates UTC time
        max_time = end_date.isoformat() + 'Z'
        eventsResult = self.gcalender.events().list(
            calendarId='primary',
            timeMin=min_time,
            timeMax=max_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return eventsResult.get('items', [])

    def retrieve_gcalendar_event_data(self, start_date, end_date, tasks_info):
        """
        Retrieve calendar events' data in TimeEntryData format
        :return: list of TimeEntryData
        """
        print('Retrieving Google Calendar events ...')
        time_entry_data_list = []

        # see https://developers.google.com/google-apps/calendar/v3/reference/events/list
        for event in self.gcalendar_events(start_date, end_date):
            start_time_str = event['start'].get('dateTime', event['start'].get('date'))
            end_time_str = event['end'].get('dateTime', event['end'].get('date'))

            (interval, start, end) = self.calc_interval(start_time_str, end_time_str)

            time_entry_data_list.append(TimeEntryData(
                year=start.year,
                month=start.month,
                day=start.day,
                interval=interval,
                comment=event['summary'],
                taskid=tasks_info['InternalMeeting']
            ))

        print('{} event found'.format(len(time_entry_data_list)))
        return time_entry_data_list

    def calc_interval(self, start_time, end_time):
        """
        :param start_time: start time in datetime
        :param end_time: end time in datetime
        :return: string hh:mm
        """
        for f in EXPECTED_DATETIME_FORMATS:
            try:
                end_dt = datetime.strptime(end_time, f)
                start_dt = datetime.strptime(start_time, f)
                t_delta_secs = (end_dt - start_dt).seconds
                return (worklog_time_spent(t_delta_secs), start_dt, end_dt)
            except Exception as e:
                pass
        print('Error: unable to parse {} and {}'.format(start_time, end_time))
        return None
