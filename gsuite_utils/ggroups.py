from __future__ import print_function
import httplib2
import os
from apiclient import discovery

from gsuite_utils.credentials import get_credentials


APP_NAME = os.path.basename(__file__).split('.')[0]

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/xxx.json
# See https://developers.google.com/admin-sdk/directory/v1/guides/authorizing
SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.user.readonly',
    'https://www.googleapis.com/auth/apps.groups.settings',
]

Defaults = {
    "DefaultGroupSettings": {
        # Some default settings are different when creating from console and from api.
        # We intend to use the same default settings as the console (as below).
        "whoCanJoin": "ALL_IN_DOMAIN_CAN_JOIN",
        "whoCanViewMembership": "ALL_IN_DOMAIN_CAN_VIEW",
        "whoCanPostMessage": "ALL_IN_DOMAIN_CAN_POST",
        "whoCanInvite": "ALL_MEMBERS_CAN_INVITE",
        "isArchived": "true",
    },
    "PublicGroupsSettings": {
        "whoCanPostMessage": "ANYONE_CAN_POST",
        "whoCanContactOwner": "ANYONE_CAN_CONTACT",
        "messageModerationLevel": "MODERATE_NONE",
        "spamModerationLevel": "ALLOW"
    },
    "Role": "MEMBER",
}

ROLES = ["OWNER", "MANAGER", "MEMBER"]


class GGroupsAndSettings(object):
    def __init__(self, client_secret_file, local_credential_file):
        self.http = self._auth(client_secret_file, local_credential_file)
        self.logs = []

    def group_info(self, group_email_address):
        """
        :param group_email_address: email address of the group
        :return: `dict` containing group basic info, settings and members
        """
        results = dict()
        results['group'] = self._get_group(group_email_address)
        if results['group'] is not None:
            results['settings'] = self._get_group_settings(group_email_address)
            results['members'] = self._get_group_members(group_email_address)
        return results

    def create_group(self, group_email_address, is_public=False):
        """
        :param group_email_address: email address of the group
        :param is_public: True if the group is public (allow posts from external email address)
        :return: `dict` containing group basic info and settings
        """
        results = dict()
        results['group'] = self._create_group(group_email_address)

        if is_public is True:
            results['settings'] = self.update_group_to_public(group_email_address)
        return results

    def update_group_settings(self, group_email_address, group_settings_dict):
        """
        :param group_email_address: email address of the group
        :param group_settings_dict: dict containing the group settings
        :return: `dict` containing group settings if succeeded; {} if no update required; None if failed.
        """
        try:
            body = {}
            groupsettings = self._get_group_settings(group_email_address)

            if groupsettings is None:
                return None

            for k, v in group_settings_dict.items():
                if groupsettings[k] != v:
                    body[k] = v

            if body:
                return self._groupssettings_service().update(groupUniqueId=group_email_address, body=body).execute()

        except Exception as e:
            self.logging('ERROR: Failed to update group settings of ({}). It is not a group or it does not exist.'
                         .format(group_email_address))
            return None
        return {}

    def update_group_to_public(self, group_email_address):
        """
        :param group_email_address: email address of the group
        :return: `dict` containing group settings if succeeded; {} if no update required; None if failed.
        """
        return self.update_group_settings(group_email_address, Defaults['PublicGroupsSettings'])

    def add_group_members(self, group_email_address, email_address_list, role=Defaults['Role']):
        """
        :param group_email_address: email address of the group
        :param email_address_list: list of email address to be added
        :return: True if succeeded; False is any failure occurred.
        """
        if role not in ROLES:
            self.logging('ERROR: Invalid role {}. Choose from {}'.format(role, ROLES))
            return False

        if not group_email_address or not email_address_list:
            self.logging('ERROR: GROUP_EMAIL_ADDRESS or MEMBER_EMAIL_ADDRESS is not provided. Nothing to remove.')
            return False

        err_cnt = 0
        for member_email_address in email_address_list:
            if self._add_group_members(group_email_address, member_email_address, role) is False:
                err_cnt += 1
        return err_cnt == 0

    def remove_group_members(self, group_email_address, email_address_list):
        """
        :param group_email_address: email address of the group
        :param email_address_list: list of email address to be removed
        :return: True if succeeded; False is any failure occurred.
        """
        if not group_email_address or not email_address_list:
            self.logging('ERROR: GROUP_EMAIL_ADDRESS or MEMBER_EMAIL_ADDRESS is not provided. Nothing to remove.')
            return False

        err_cnt = 0
        for member_email_address in email_address_list:
            if self._remove_group_members(group_email_address, member_email_address) is False:
                err_cnt += 1
        return err_cnt == 0

    def _add_group_members(self, group_email_address, member_email_address, role):
        """
        :param group_email_address: email address of the group
        :param email_address_list: list of email address to be added
        :return: True if succeeded; False is any failure occurred.
        """
        try:
            body = {'email': member_email_address, 'role': role}
            self._members_service().insert(groupKey=group_email_address, body=body).execute()

        except Exception as e:
            if 'Resource Not Found: groupKey' in str(e):
                msg = "Group not found."
            elif 'already exist' in str(e):
                msg = 'Already exist.'
            elif 'Invalid Input: memberKey' in str(e):
                msg = '{} cannot be added as {}.'.format(member_email_address, role)
            else:
                msg = e
            self.logging('ERROR: Failed to add {} {} to {}. {}'.format(
                role, member_email_address, group_email_address, msg))
            return False
        return True

    def _remove_group_members(self, group_email_address, member_email_address):
        """
        :param group_email_address: email address of the group
        :param email_address_list: list of email address to be removed
        :return: True if succeeded; False is any failure occurred.
        """
        try:
            self._members_service().delete(groupKey=group_email_address, memberKey=member_email_address).execute()

        except Exception as e:
            if 'Resource Not Found: groupKey' in str(e):
                msg = "Group not found."
            elif 'Resource Not Found: memberKey' in str(e) or 'Missing required field: memberKey' in str(e):
                msg = "Member not found."
            else:
                msg = e
            self.logging('ERROR: Failed to remove {} from {}. {}'.format(
                member_email_address, group_email_address, msg))
            return False
        return True

    @staticmethod
    def is_group_public(groupsettings):
        """Return True if it is a public group (allowing posts from external email address)
        """
        return groupsettings["whoCanPostMessage"] == Defaults["PublicGroupsSettings"]["whoCanPostMessage"]

    def _get_group(self, group_email_address):
        """
        :param group_email_address: email address of the group
        :return:
          Response in a dict with group information if request succeeded;
          None if group_email_address is None or empty
        """
        try:
            return self._groups_service().get(groupKey=group_email_address).execute()

        except Exception as e:
            msg = 'Group not found.' if 'Resource Not Found' in str(e) else e
            self.logging('ERROR: Failed to retrieve group ({}). {}'.format(group_email_address, msg))
            return None

    def _create_group(self, group_email_address):
        """Create a new Group.
        :param group_email_address: email address of the group
        :return: Group payload in `dict` or None if failed to create the group.
        """
        body = {
            "email": group_email_address,
            "name": group_email_address
        }
        try:
            return self._groups_service().insert(body=body).execute()
        except Exception as e:
            msg = 'Group already exist.' if 'Entity already exist' in str(e) else e
            self.logging('ERROR: Failed to create group ({}). {}'.format(group_email_address, msg))
            return None

    def _get_group_settings(self, group_email_address):
        """Return group settings
        """
        max_try=3
        attempt = 1
        while attempt <= max_try:
            try:
                return self._groupssettings_service().get(groupUniqueId=group_email_address, alt='json').execute()

            except Exception as e:
                # try again, sometimes google returns 'server issue" when retrieving group settings
                attempt += 1
                if attempt > max_try:
                    msg = 'Not exist or not a group.' if 'Backend Error' in str(e) else e
                    self.logging('ERROR: Failed to retrieve group settings of ({}). {}'.format(group_email_address, msg))
        return None

    def _get_group_members(self, group_email_address):
        """
        :param group_email_address: email address of the group
        :return: list of members in list of {email, role, type, status, etc.}
        """
        try:
            results = self._members_service().list(groupKey=group_email_address).execute()
            return results.get('members', [])

        except Exception as e:
            self.logging('ERROR: {}'.format(e))
            return None

    @staticmethod
    def _auth(client_secret_file, local_credential_file):
        return get_credentials(
            application_name=APP_NAME,
            client_secret_file=client_secret_file,
            local_credential_file=local_credential_file,
            scopes=SCOPES,
        ).authorize(httplib2.Http())

    def _groups_service(self):
        # https://developers.google.com/resources/api-libraries/documentation/admin/directory_v1/python/latest/admin_directory_v1.groups.html
        service = discovery.build('admin', 'directory_v1', http=self.http)
        return service.groups()

    def _groupssettings_service(self):
        # see https://developers.google.com/resources/api-libraries/documentation/groupssettings/v1/python/latest/groupssettings_v1.groups.html
        service = discovery.build('groupssettings', 'v1', http=self.http)
        return service.groups()

    def _members_service(self):
        # https://developers.google.com/resources/api-libraries/documentation/admin/directory_v1/python/latest/admin_directory_v1.members.html
        service = discovery.build('admin', 'directory_v1', http=self.http)
        return service.members()

    def logging(self, msg):
        self.logs.append(msg)
