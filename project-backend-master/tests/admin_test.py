import pytest, requests
from src.config import url

############################ TEST SET UP ############################

@pytest.fixture
def user_1():
    requests.delete(f'{url}clear/v1')
    data_obj = {
        'email': 'email1@gmail.com', 
        'password': 'password1',
        'name_first': 'User', 
        'name_last': 'First'
    }
    response = requests.post(f'{url}auth/register/v2', json = data_obj)
    return response.json()

@pytest.fixture
def user_2():
    data_obj = {
        'email': 'email2@gmail.com', 
        'password': 'password2',
        'name_first': 'User', 
        'name_last': 'Second'
    }
    response = requests.post(f'{url}auth/register/v2', json = data_obj)
    return response.json()

@pytest.fixture
def user_3():
    data_obj = {
        'email': 'email3@gmail.com', 
        'password': 'password3',
        'name_first': 'User', 
        'name_last': 'Third',
    }
    response = requests.post(f'{url}auth/register/v2', json = data_obj)
    return response.json()

############################ CHANGE USER PERM ############################

# Testing normal functionality of changing user permission
def test_change_permission(user_1, user_2):

    # Change user 2's permission to admin
    requests.post(f'{url}admin/userpermission/change/v1', json={
        'token': user_1['token'],
        'u_id': user_2['auth_user_id'],
        'permission_id': 1}
    )

    # Create private channel
    c = requests.post(f'{url}channels/create/v2', json={
        'token': user_1['token'],
        'name': 'channel',
        'is_public': False}
    )
    channel = c.json()

    # User 2 joins private channel
    requests.post(f'{url}channel/join/v2', json={
        'token': user_2['token'],
        'channel_id': channel['channel_id']
    })
    
    # Grab details of channel members and check
    members = requests.get(f'{url}channel/details/v2', params={
        'token': user_2['token'],
        'channel_id': channel['channel_id']}
    )
    memberlist = members.json()

    assert {
        'name_first': 'User', 
        'name_last': 'Second', 
        'email': 'email2@gmail.com', 
        'handle_str': 'usersecond',
        'u_id': user_2['auth_user_id'],
        'profile_img_url': f'{url}profileAvatar/default',
    } in memberlist['all_members']

    # User 2 gives himself channel owner
    requests.post(f'{url}channel/addowner/v1', json={
        'token': user_2['token'],
        'channel_id': channel['channel_id'],
        'u_id': user_2['auth_user_id']
    })

    # Grab list of owners and check user 2 is in
    owners = requests.get(f'{url}channel/details/v2', params={
        'token': user_2['token'],
        'channel_id': channel['channel_id']}
    )
    ownerlist = owners.json()

    assert {
        'name_first': 'User', 
        'name_last': 'Second', 
        'email': 'email2@gmail.com', 
        'handle_str': 'usersecond',
        'u_id': user_2['auth_user_id'],
        'profile_img_url': f'{url}profileAvatar/default'
    } in ownerlist['owner_members']


# Access Error when unauthorised user tries to change permissions
def test_invalid_permission(user_1, user_2):
    response2 = requests.post(f'{url}admin/userpermission/change/v1', json={
        'token': user_2['token'],
        'u_id': user_1['auth_user_id'],
        'permission_id': 2}
    )
    assert response2.status_code == 403


# Input Error when target user doesn't exist (i.e. u_id doesn't exist)
def test_invalid_target(user_1):
    response = requests.post(f'{url}admin/userpermission/change/v1', json={
        'token': user_1['token'],
        'u_id': -1,
        'permission_id': 2}
    )
    assert response.status_code == 400


# Input Error when an invalid permission id is input
def test_invalid_permid(user_1, user_2):
    response = requests.post(f'{url}admin/userpermission/change/v1', json={
        'token': user_1['token'],
        'u_id': user_2['auth_user_id'],
        'permission_id': 3}
    )
    assert response.status_code == 400


# Input Error when target user already has the target permission id
def test_same_permission(user_1, user_2):
    response = requests.post(f'{url}admin/userpermission/change/v1', json={
        'token': user_1['token'],
        'u_id': user_2['auth_user_id'],
        'permission_id': 2}
    )
    assert response.status_code == 400


# Input Error when the last authorised user tries to demote themselves
def test_lastowner_demote(user_1):
    response = requests.post(f'{url}admin/userpermission/change/v1', json={
        'token': user_1['token'],
        'u_id': user_1['auth_user_id'],
        'permission_id': 2}
    )
    assert response.status_code == 400

############################ ADMIN USER REMOVE ############################


# Test functionality of removing user attributes
def test_user_remove(user_1, user_2):
    # Remove user 2
    requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user_1['token'],
        'u_id': user_2['auth_user_id']}
    )

    # Check user profile is still callable
    response1 = requests.get(f'{url}user/profile/v1', params={
        'token': user_1['token'],
        'u_id': user_2['auth_user_id']}
    )
    user_details = response1.json()

    assert user_details['user'] == {
        'name_first': 'Removed',
        'name_last': 'user',
        'email': '',
        'u_id': user_2['auth_user_id'],
        'handle_str':'',
        'profile_img_url': f'{url}profileAvatar/default'
    }

    # Check user 2 is not listed on all-users list
    response2 = requests.get(f'{url}users/all/v1', params={'token': user_1['token']})
    expected_list = [{
        'name_first': 'User',
        'name_last': 'First',
        'email': 'email1@gmail.com',
        'u_id': user_1['auth_user_id'],
        'handle_str': 'userfirst',
        'profile_img_url': f'{url}profileAvatar/default'
    }]

    assert response2.json()['users'] == expected_list

# Check deleted User's email & handle can be re-used
def test_user_identifier_reusability(user_1, user_2):
    # Remove user 2
    requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user_1['token'],
        'u_id': user_2['auth_user_id']}
    )

    # Register user with same handle as user 2
    data_obj = {
        'email': 'email2@gmail.com', 
        'password': 'password2',
        'name_first': 'Use', 
        'name_last': 'RSecond'
    }
    response = requests.post(f'{url}auth/register/v2', json = data_obj)
    tmp_user_id = response.json()['auth_user_id']

    # Check handle is correct
    response = requests.get(f'{url}user/profile/v1', params={
        'token': user_1['token'],
        'u_id': tmp_user_id}
    )
    assert response.json()['user'] == {
        'name_first': 'Use',
        'name_last': 'RSecond',
        'email': 'email2@gmail.com',
        'u_id': tmp_user_id,
        'handle_str':'usersecond',
        'profile_img_url': f'{url}profileAvatar/default'
    }

    # Create another user with same handle
    data_obj = {
        'email': 'email8@gmail.com', 
        'password': 'password2',
        'name_first': 'User', 
        'name_last': 'Second'
    }
    response = requests.post(f'{url}auth/register/v2', json = data_obj)
    tmp_user_id = response.json()['auth_user_id']
    
    # Check handle is correct
    response = requests.get(f'{url}user/profile/v1', params={
        'token': user_1['token'],
        'u_id': tmp_user_id}
    )
    assert response.json()['user'] == {
        'name_first': 'User',
        'name_last': 'Second',
        'email': 'email8@gmail.com',
        'u_id': tmp_user_id,
        'handle_str':'usersecond0',
        'profile_img_url': f'{url}profileAvatar/default'
    }


# Test functionality of member removal from channel
def test_member_removed_from_channel(user_1, user_2):

    # Authorised user creates channel
    c = requests.post(f'{url}channels/create/v2', json={
        'token': user_1['token'],
        'name': 'channel',
        'is_public': True}
    )

    # Create another channel to test for user 2 not being in channel
    requests.post(f'{url}channels/create/v2', json={
        'token': user_1['token'],
        'name': 'dummy_channel',
        'is_public': False}
    )

    channel = c.json()

    # User joins channel
    requests.post(f'{url}channel/join/v2', json={
        'token': user_2['token'],
        'channel_id': channel['channel_id']
    })
    
    # Retrieve channel details for member list
    response = requests.get(f'{url}channel/details/v2', params={
        'token': user_1['token'],
        'channel_id': channel['channel_id']}
    )

    memberlist = response.json()

    # Check the added member exists within the channel
    assert {
        'name_first': 'User', 
        'name_last': 'Second', 
        'email': 'email2@gmail.com', 
        'handle_str': 'usersecond',
        'u_id': user_2['auth_user_id'],
        'profile_img_url': f'{url}profileAvatar/default'
    } in memberlist['all_members']

    # Remove user
    requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user_1['token'],
        'u_id': user_2['auth_user_id']}
    )

    # Retrieve information again (updated)
    response = requests.get(f'{url}channel/details/v2', params={
        'token': user_1['token'],
        'channel_id': channel['channel_id']}
    )

    memberlist = response.json()

    # Check the added member is no longer within the channel
    assert {
        'name_first': 'User', 
        'name_last': 'Second', 
        'email': 'email2@gmail.com', 
        'handle_str': 'usersecond',
        'u_id': user_2['auth_user_id'],
        'profile_img_url': f'{url}profileAvatar/default'
    } not in memberlist['all_members']


# Test functionality of owner removal from channel and dm
def test_owner_removed_channel_DM(user_1, user_3):

    # Authorised user creates channel
    c = requests.post(f'{url}channels/create/v2', json={
        'token': user_1['token'],
        'name': 'channel',
        'is_public': True}
    )
    channel = c.json()

    # Create DM that creator will be removed later on
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user_3['token'],
        "u_ids": [user_1['auth_user_id']]
    })

    dm = response.json()

    # Create empty DM to check False Condition of user 3 being in DM
    requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": []
    })

    # Create messages that creator will be removed later on
    message_1 = {
        'token': user_3['token'],
        'dm_id': dm['dm_id'],
        'message': "Morris, Michael, Param and Roland",
    }
    message_2 = {
        'token': user_1['token'],
        'dm_id': dm['dm_id'],
        'message': "Holy Moly Crackamoly",
    }

    requests.post(f'{url}/message/senddm/v1', json = message_1)
    requests.post(f'{url}/message/senddm/v1', json = message_2)

    # Give user 3 admin perms
    requests.post(f'{url}admin/userpermission/change/v1', json={
        'token': user_1['token'],
        'u_id': user_3['auth_user_id'],
        'permission_id': 1}
    )

    # Owner joins channel (so len(global_owner) == 2)
    requests.post(f'{url}channel/join/v2', json={
        'token': user_3['token'],
        'channel_id': channel['channel_id']
    })

    # Adds himself as channel owner
    requests.post(f'{url}channel/addowner/v1', json = {
        'token': user_3['token'],
        'channel_id': channel['channel_id'],
        'u_id': user_3['auth_user_id']
    })

    # Retrieve channel details for owner list
    response = requests.get(f'{url}channel/details/v2', params={
        'token': user_1['token'],
        'channel_id': channel['channel_id']}
    )
    ownerlist = response.json()

    # Check the added owner exists within the channel
    assert {
        'name_first': 'User', 
        'name_last': 'Third', 
        'email': 'email3@gmail.com', 
        'handle_str': 'userthird',
        'u_id': user_3['auth_user_id'],
        'profile_img_url': f'{url}profileAvatar/default'
    } in ownerlist['owner_members']

    # Remove the owner
    requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user_1['token'],
        'u_id': user_3['auth_user_id']}
    )

    # Retrieve channel details for owner list again
    response = requests.get(f'{url}channel/details/v2', params={
        'token': user_1['token'],
        'channel_id': channel['channel_id']}
    )
    ownerlist = response.json()

    # Check the added owner is no longer within the channel
    assert {
        'name_first': 'User', 
        'name_last': 'Third', 
        'email': 'email3@gmail.com', 
        'handle_str': 'userthird',
        'u_id': user_3['auth_user_id'],
        'profile_img_url': f'{url}profileAvatar/default'
    } not in ownerlist['owner_members']

    # Check user_3 in DM got removed
    response = requests.get(
        f"{url}dm/details/v1", 
        params = {'token': user_1['token'], 'dm_id': dm['dm_id']}
    )
    required_output = { 
        'name': 'userfirst, userthird',
        'members': [{
            'u_id': user_1['auth_user_id'],
            'name_first': 'User',
            'name_last': "First",
            'email': "email1@gmail.com",
            'handle_str': 'userfirst',
            'profile_img_url': f'{url}profileAvatar/default'
        }],
    }
    assert response.json() == required_output

    # Check messages got removed
    response = requests.get(f'{url}dm/messages/v1', {
        'token': user_1['token'],
        'dm_id': dm['dm_id'],
        'start': 0
    })
    assert response.json()['messages'][1]['message'] == 'Removed user'


# Access Error when user calling function is unauthorised
def test_unauthorised_user(user_1, user_2):
    response = requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user_2['token'],
        'u_id': user_1['auth_user_id']}
    )
    assert response.status_code == 403


# Input Error when the last authorised user tries to remove themself
def test_owner_remove_self(user_1):
    response1 = requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user_1['token'],
        'u_id': user_1['auth_user_id']}
    )
    assert response1.status_code == 400

# Test removed user cannot login
def test_removed_user_login(user_1, user_2):
    requests.delete(f'{url}admin/user/remove/v1', json={
        'token': user_1['token'],
        'u_id': user_2['auth_user_id']}
    )

    # Test user removed already auto-logout
    response = requests.post(f'{url}auth/logout/v1', json = {'token': user_2['token']})
    assert response.status_code == 403

    # Case where old email/pass does not work
    data_obj = {
        'email': 'email2@gmail.com', 
        'password': 'password2',
    }
    fail_1 = requests.post(f'{url}auth/login/v2',json = data_obj)
    assert fail_1.status_code == 400

    # Case where user cannot login using empty email and password
    data_obj = {
        'email': '', 
        'password': '',
    }
    fail_2 = requests.post(f'{url}auth/login/v2',json = data_obj)
    assert fail_2.status_code == 400
