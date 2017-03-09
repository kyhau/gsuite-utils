"""
Test gsuite_utils.ggroups
"""
import pytest
from mock import Mock

from gsuite_utils.ggroups import GGroupsAndSettings

MOCK_GROUP = {
    'kind': 'admin#directory#group', 'name': 'group1@example.com', 'adminCreated': True,
    'directMembersCount': '2', 'email': 'group1@example.com', 'etag': '"xxx"', 
    'aliases': ['group2@example.com'], 'id': 'xxx', 'description': ''
}

MOCK_GROUP_SETTINGS = {
    'allowExternalMembers': 'false', 'whoCanJoin': 'CAN_REQUEST_TO_JOIN',
    'whoCanViewMembership': 'ALL_IN_DOMAIN_CAN_VIEW', 'includeCustomFooter': 'false',
    'defaultMessageDenyNotificationText': u'', 'includeInGlobalAddressList': 'true',
    'archiveOnly': 'false', 'isArchived': 'true', 'membersCanPostAsTheGroup': 'false',
    'allowWebPosting': 'true', 'email': 'group1@example.com',
    'messageModerationLevel': 'MODERATE_NONE', 'description': '',
    'replyTo': 'REPLY_TO_IGNORE', 'customReplyTo': '', 'sendMessageDenyNotification': 'false',
    'whoCanContactOwner': 'ANYONE_CAN_CONTACT', 'messageDisplayFont': 'DEFAULT_FONT',
    'whoCanLeaveGroup': 'ALL_MEMBERS_CAN_LEAVE', 'whoCanAdd': 'ALL_MANAGERS_CAN_ADD',
    'whoCanPostMessage': 'ANYONE_CAN_POST', 'name': 'group1@example.com',
    'kind': 'groupsSettings#groups', 'whoCanInvite': 'ALL_MANAGERS_CAN_INVITE',
    'spamModerationLevel': 'ALLOW', 'whoCanViewGroup': 'ALL_IN_DOMAIN_CAN_VIEW',
    'showInGroupDirectory': 'false', 'maxMessageBytes': 26214400, 'customFooterText': '',
    'allowGoogleCommunication': 'false'
}

MOCK_MEMBERS = {
    'kind': 'admin#directory#members',
    'etag': '"xxx"',
    'members': [
        {'email': 'user1@example.com', 'role': 'OWNER', 'type': 'USER', 'status': 'ACTIVE', 'kind': 'admin#directory#member', 'id': '111', 'etag': '"x111"'},
        {'email': 'user2@example.com', 'role': 'MANAGER', 'type': 'USER', 'status': 'ACTIVE', 'kind': 'admin#directory#member', 'id': '222', 'etag': '"x222"'},
        {'email': 'user3@example.com', 'role': 'MEMBER', 'type': 'USER', 'status': 'ACTIVE', 'kind': 'admin#directory#member', 'id': '333', 'etag': '"x333"'},
        {'email': 'group1@example.com', 'role': 'MEMBER', 'type': 'GROUP', 'status': 'ACTIVE','kind': 'admin#directory#member', 'id': '444', 'etag': '"x444"'},
    ]
}


@pytest.fixture(scope='function')
def mock_helper():
    # Mock required objects requiring auth
    GGroupsAndSettings._auth = Mock(return_value=None)
    helper = GGroupsAndSettings(
        client_secret_file="sample_not_exist.json",
        local_credential_file="sample_not_exist.json",
    )
    return helper


def test_group_info(mock_helper):
    """
    Test GGroupsAndSettings.group_info
    """
    helper = mock_helper
    helper._get_group = Mock(return_value=MOCK_GROUP)
    helper._get_group_settings = Mock(return_value=MOCK_GROUP_SETTINGS)
    helper._get_group_members = Mock(return_value=MOCK_MEMBERS)

    email_addr = "test_group@example.com"
    ret = helper.group_info(email_addr)

    assert ret['group']
    assert ret['settings']
    assert ret['members']
    assert helper.logs == []


def test_create_group(mock_helper):
    """
    Test GGroupsAndSettings.create_group
    """
    helper = mock_helper
    email_addr = "test_group@example.com"

    # case 1: public, pass
    helper._create_group = Mock(return_value=MOCK_GROUP)
    helper.update_group_settings = Mock(return_value=MOCK_GROUP_SETTINGS)
    MOCK_GROUP_SETTINGS["whoCanPostMessage"] = ""

    ret = helper.create_group(email_addr, is_public=True)
    assert ret['group']
    assert ret['settings']

    # case 2: not public, pass
    helper._create_group = Mock(return_value=MOCK_GROUP)
    helper.update_group_settings = Mock(return_value=None)

    ret = helper.create_group(email_addr)
    assert ret['group']
    assert 'settings' not in ret.keys()

    # case 3: not public, fail
    helper._create_group = Mock(return_value=MOCK_GROUP)
    helper.update_group_settings = Mock(return_value=None)

    ret = helper.create_group(email_addr, is_public=False)
    assert ret['group']
    assert 'settings' not in ret.keys()


def test_add_group_members(mock_helper):
    """
    Test GGroupsAndSettings.add_group_members
    """
    helper = mock_helper
    g_email_addr = "test_group@example.com"
    u_email_addr = "test_user@example.com"

    # case 1: pass
    helper._add_group_members = Mock(return_value=True)

    assert True == helper.add_group_members(g_email_addr, u_email_addr)

    # case 2: invalid role so fail
    helper._add_group_members = Mock(return_value=True)

    assert False == helper.add_group_members(g_email_addr, u_email_addr, role="ABC")

    # case 3: valid role but fail
    helper._add_group_members = Mock(return_value=False)

    assert False == helper.add_group_members(g_email_addr, u_email_addr)


def test_remove_group_members(mock_helper):
    """
    Test GGroupsAndSettings.remove_group_members
    """
    helper = mock_helper
    g_email_addr = "test_group@example.com"
    u_email_addr = "test_user@example.com"

    # case 1: pass
    helper._remove_group_members = Mock(return_value=True)

    assert True == helper.remove_group_members(g_email_addr, u_email_addr)

    # case 2: fail
    helper._remove_group_members = Mock(return_value=False)

    assert False == helper.remove_group_members(g_email_addr, u_email_addr)
