import pytest, requests
from src.config import url

############################ TEST SET UP ############################

@pytest.fixture
def user_1():
    requests.delete(f'{url}clear/v1')
    data_obj = {
        'email': 'email0@gmail.com', 
        'password': 'password0',
        'name_first': 'User', 
        'name_last': 'First'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    return response.json()


@pytest.fixture
def user_2():
    data_obj = {
        'email': 'email1@gmail.com', 
        'password': 'password1',
        'name_first': 'User', 
        'name_last': 'Second'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    return response.json()


@pytest.fixture
def c_1(user_1):
    data_obj_1= {
    'token': user_1['token'],
    'name': 'FlandreScarlet', 
    'is_public': False,
    }
    response = requests.post(f'{url}channels/create/v2', json = data_obj_1).json()

    return [user_1, response]


@pytest.fixture
def c_2(user_2):
    data_obj_1 = {
    'token': user_2['token'],
    'name': 'vampire', 
    'is_public': True,
    }
    response = requests.post(f'{url}channels/create/v2', json = data_obj_1).json()

    return [user_2, response]

############################ TEST CHANNEL INVITE/JOIN ############################

def test_join_invite(c_1, c_2):

    token1 = c_1[0]['token']
    u_id1 = c_1[0]['auth_user_id']
    c_id1 = c_1[1]['channel_id']
    
    token2 = c_2[0]['token']
    u_id2 = c_2[0]['auth_user_id']
    c_id2 = c_2[1]['channel_id']
    
    # User 1 join channel 2
    requests.post(f'{url}channel/join/v2', json = {
        'token': token1,
        'channel_id': c_id2
    })

    # Get channel 2 details
    response = requests.get(f'{url}channel/details/v2', {
        'token': token1,
        'channel_id': c_id2
    })
    channel_2 = response.json()
    
    # Get user 1 profile
    response = requests.get(f'{url}user/profile/v1', {'token': token1, 'u_id': u_id1})
    user1_info = response.json()

    # Check user is in channel, name and is_public is correct
    assert channel_2['name'] == 'vampire'
    assert channel_2['is_public'] == True
    assert user1_info['user'] in channel_2['all_members']

    # User 1 invite user 2 into channel 1
    requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })

    # Get user 2 profile
    response = requests.get(f'{url}user/profile/v1', 
        {'token': token2, 'u_id': u_id2})
    user2_info = response.json()

    # Get channel 1 details
    response = requests.get(f'{url}channel/details/v2', {
        'token': token2,
        'channel_id': c_id1
    })
    channel_1 = response.json()

    # Check channel details are correct
    assert channel_1['name'] == 'FlandreScarlet'
    assert channel_1['is_public'] == False
    assert user2_info['user'] in channel_1['all_members']


# Invalid channel detail cases
def test_invalid_channel_details(c_1, c_2):

    token1 = c_1[0]['token']
    c_id2 = c_2[1]['channel_id']
    
    # AccessError: User 1 not in channel 2
    response = requests.get(f'{url}channel/details/v2', {
        'token': token1,
        'channel_id': c_id2
    })
    assert response.status_code == 403

    # InputError: Invalid channel ID
    response = requests.get(f'{url}channel/details/v2', {
        'token': token1,
        'channel_id': 3123
    })
    assert response.status_code == 400


# Test invalid join cases
def test_channel_join_invalid(c_1, c_2):

    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    token2 = c_2[0]['token']

    # InputError: Already in channel
    response =requests.post(f'{url}channel/join/v2', json = {
        'token': token1,
        'channel_id': c_id1
    })
    response.status_code == 400

    # InputError: Invalid c_id
    response =requests.post(f'{url}channel/join/v2', json = {
        'token': token1,
        'channel_id': 999
    })
    response.status_code == 400

    # AccessError: Normal user cannot join private channel
    response =requests.post(f'{url}channel/join/v2', json = {
        'token': token2,
        'channel_id': c_id1
    })
    response.status_code == 403


# Invite invalid cases
def test_channel_invite_invalid(c_1, c_2):

    token1 = c_1[0]['token']
    u_id1 = c_1[0]['auth_user_id']
    c_id1 = c_1[1]['channel_id']
    token2 = c_2[0]['token']
    u_id2 = c_2[0]['auth_user_id']

    # InputError: Cannot invite themselves
    response =requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id1
    })
    response.status_code == 400

    # InputError: Cannot invite invalid c_id
    response =requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': 999,
        'u_id': u_id2

    })
    response.status_code == 400

    # InputError: Invalid u_id
    response =requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': 69

    })
    response.status_code == 400

    # AccessError: Non-channel member cannot invite to that channel
    response =requests.post(f'{url}channel/invite/v2', json = {
        'token': token2,
        'channel_id': c_id1,
        'u_id': u_id2
    })
    response.status_code == 403

############################ TEST CHANNEL LEAVE/ADDOWNER/REMOVEOWNER ############################

# Test leave valid
def test_channel_leave(c_1, c_2):

    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    
    token2 = c_2[0]['token']
    u_id2 = c_2[0]['auth_user_id']

    # Invite user 2
    requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })

    # Get channel info
    response = requests.get(f'{url}channel/details/v2', {
        'token': token2,
        'channel_id': c_id1
    })
    channel_1 = response.json()
    
    # Get user info
    response = requests.get(f'{url}user/profile/v1', 
        {'token': token2, 'u_id': u_id2})
    user2_info = response.json()

    # Check user is in channel member list
    assert user2_info['user'] in channel_1['all_members']
    
    # User 2 leaves channel 1
    requests.post(f'{url}channel/leave/v1', json = {
        'token': token2,
        'channel_id': c_id1
    })

    # Get channel 1 details updated
    response = requests.get(f'{url}channel/details/v2', {
        'token': token1,
        'channel_id': c_id1
    })
    channel_1 = response.json()

    # User 2 should not be in channel anymore
    assert user2_info['user'] not in channel_1['all_members']


# Test channel owner leaving
def test_owner_leave(c_1, c_2):

    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    
    token2 = c_2[0]['token']
    u_id2 = c_2[0]['auth_user_id']

    # Invite user 2
    requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })

    # Add user 2 as channel owner
    requests.post(f'{url}channel/addowner/v1', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })

    # Get channel 1 details
    response = requests.get(f'{url}channel/details/v2', {
        'token': token2,
        'channel_id': c_id1
    })
    channel_1 = response.json()
    
    # Get user 2 details and check channel members
    response = requests.get(f'{url}user/profile/v1', 
        {'token': token2, 'u_id': u_id2})
    user2_info = response.json()
    assert user2_info['user'] in channel_1['owner_members']
    
    # User 2 leaves channel 1
    requests.post(f'{url}channel/leave/v1', json = {
        'token': token2,
        'channel_id': c_id1
    })

    # Get channel 1 updated details
    response = requests.get(f'{url}channel/details/v2', {
        'token': token1,
        'channel_id': c_id1
    })
    channel_1 = response.json()

    # Check removal from owner list
    assert user2_info['user'] not in channel_1['owner_members']


# Test invalid leave cases
def test_invalid_channel_leave(c_1, c_2):
    
    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    token2 = c_2[0]['token']

    # InputError: Invalid c_id
    response = requests.post(f'{url}channel/leave/v1', json = {
        'token': token1,
        'channel_id': 711
    })
    response.status_code == 400
    
    # AccessError: Cannot leave channel they're not in
    response = requests.post(f'{url}channel/leave/v1', json = {
        'token': token2,
        'channel_id': c_id1
    })
    response.status_code == 403


# Test adding user to channel owner functionality
def test_add_owner(c_1, c_2):

    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    u_id2 = c_2[0]['auth_user_id']

    # Invite user 2
    requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })

    # Add user 2 to owner
    requests.post(f'{url}channel/addowner/v1', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })

    # Check owner members = all members to show user 2 is now owner
    response = requests.get(f'{url}channel/details/v2', {
        'token': token1,
        'channel_id': c_id1
    })
    assert response.json()['owner_members'] == response.json()['all_members']


# Test invalid add_owner cases
def test_add_owner_invalid(c_1, c_2):

    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    token2 = c_2[0]['token']
    u_id2 = c_2[0]['auth_user_id']

    # InputError: Invalid channel
    response = requests.post(f'{url}channel/addowner/v1', json = {
        'token': token1,
        'channel_id': 972,
        'u_id': u_id2
    })
    assert response.status_code == 400

    # InputError: Invalid user id
    response = requests.post(f'{url}channel/addowner/v1', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': 101
    })
    assert response.status_code == 400

    # InputError: User not in channel
    response = requests.post(f'{url}channel/addowner/v1', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })
    assert response.status_code == 400

    # Invite user 2 to channel 1
    requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })

    # AccessError: Auth user do not have owner permission
    response = requests.post(f'{url}channel/addowner/v1', json = {
        'token': token2,
        'channel_id': c_id1,
        'u_id': u_id2
    })
    assert response.status_code == 403

    requests.post(f'{url}channel/addowner/v1', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })

    # InputError: User already a owner of channel
    response = requests.post(f'{url}channel/addowner/v1', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })
    assert response.status_code == 400


# Test remove owner from channel functionality
def test_remove_owner(c_1, c_2):

    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    u_id2 = c_2[0]['auth_user_id']  

    # Invite user 2
    requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })    
    response = requests.get(f'{url}channel/details/v2', {
        'token': token1,
        'channel_id': c_id1
    })
    origin_info = response.json()

    # Add user 2 as owner of channel
    requests.post(f'{url}channel/addowner/v1', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })

    # Remove user 2 as owner
    requests.post(f'{url}channel/removeowner/v1', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })

    # Check owner list is same as original
    response = requests.get(f'{url}channel/details/v2', {
        'token': token1,
        'channel_id': c_id1
    })
    assert response.json()['owner_members'] == origin_info['owner_members']


# Invalid remove owner cases
def test_remove_owner_invalid(c_1, c_2):

    token1 = c_1[0]['token']
    token2 = c_2[0]['token']
    u_id1 = c_1[0]['auth_user_id']
    c_id1 = c_1[1]['channel_id']
    u_id2 = c_2[0]['auth_user_id']  

    # Invite user 2
    requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })    

    # InputError: Invalid channel
    response = requests.post(f'{url}channel/removeowner/v1', json = {
        'token': token1,
        'channel_id': 851,
        'u_id': u_id2
    })
    assert response.status_code == 400

    # InputError: Invalid user
    response = requests.post(f'{url}channel/removeowner/v1', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': 109
    })
    assert response.status_code == 400     

    # InputError: User not an owner of channel
    response = requests.post(f'{url}channel/removeowner/v1', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })
    assert response.status_code == 400   

    # InputError: Remove the only owner of channel
    response = requests.post(f'{url}channel/removeowner/v1', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id1
    })
    assert response.status_code == 400

    # AccessError: Auth user do not have owner permission
    response = requests.post(f'{url}channel/removeowner/v1', json = {
        'token': token2,
        'channel_id': c_id1,
        'u_id': u_id1
    })
    assert response.status_code == 403

############################ TEST CHANNEL MESSAGES ############################

# Test channel messages functionality
def test_channel_messages(c_1, c_2, user_1, user_2):

    token1 = c_1[0]['token']
    uid_1 = c_1[0]['auth_user_id']
    c_id1 = c_1[1]['channel_id']
    token2 = c_2[0]['token']
    c_id2 = c_2[1]['channel_id']
    
    # Send message 1
    message_1 = {
        'token': token1,
        'channel_id': c_id1,
        'message': "Morris, Michael, Param and Roland",
        }
    response = requests.post(f'{url}message/send/v1', json = message_1)
    m_id1 = response.json()['message_id']

    # Send message 2
    message_2 = {
        'token': token1,
        'channel_id': c_id1,
        'message': "Anyone up for KFC?" 
        }
    response = requests.post(f'{url}message/send/v1', json = message_2)
    m_id2 = response.json()['message_id']

    # Assert messages are inserted into store in correct order
    assert m_id1 < m_id2

    # Create fake message for filtering
    message_fake = {
        'token': token2,
        'channel_id': c_id2,
        'message': "Bam and the dirt is gone" 
        }
    response = requests.post(f'{url}message/send/v1', json = message_fake)

    # Create dummy DM
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user_2['token'],
        "u_ids": [user_1['auth_user_id']]
    })
    dm = response.json()

    # Create messages to make sure messages function returns channel messages only
    message_3 = {
        'token': user_2['token'],
        'dm_id': dm['dm_id'],
        'message': "Yea the boys",
    }
    requests.post(f'{url}message/senddm/v1', json = message_3)

    # Call channel messages
    response = requests.get(f'{url}channel/messages/v2', {
        'token': token1,
        'channel_id': c_id1,
        'start': 0
    })

    # Test return -1 when reach the end, return order of message list
    assert response.json()['end'] == -1
    assert response.json()['messages'][0]['message'] == 'Anyone up for KFC?'
    assert response.json()['messages'][0]['u_id'] == uid_1
    assert response.json()['messages'][1]['message'] == 'Morris, Michael, Param and Roland'

    # Test return start + 50 for end when not reach the end (i.e. end != -1)
    i = 0
    while i < 52:
        requests.post(f'{url}message/send/v1', json = message_2)
        i += 1
    response = requests.get(f'{url}channel/messages/v2', {
        'token': token1,
        'channel_id': c_id1,
        'start': 3
    })
    assert response.json()['end'] == 53
    assert len(response.json()['messages']) == 50


# Invalid channel message call
def test_invalid_channel_messages(c_1, c_2):
    
    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    token2 = c_2[0]['token']

    # InputError: Invalid start number
    response = requests.get(f'{url}channel/messages/v2', {
        'token': token1,
        'channel_id': c_id1,
        'start': 1
    })
    assert response.status_code == 400

    # InputError: Invalid channel ID
    response = requests.get(f'{url}channel/messages/v2', {
        'token': token1,
        'channel_id': 88,
        'start': 0
    })
    assert response.status_code == 400

    # AccessError: Invalid auth user
    response = requests.get(f'{url}channel/messages/v2', {
        'token': token2,
        'channel_id': c_id1,
        'start': 0
    })
    assert response.status_code == 403