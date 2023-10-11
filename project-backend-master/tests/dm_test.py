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
        'name_last': 'Third'
    }
    response = requests.post(f'{url}auth/register/v2', json = data_obj)
    return response.json()


############################ TEST DM CREATE ############################

# Check DM is created
def test_dm_create(user_1, user_2):
    response0 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    create_dm = response0.json()
    assert create_dm == {
        'dm_id': 0,
    }

# InputError: any u_id in u_ids does not refer to a valid user
def test_dm_create_invalid_uid(user_1, user_2):
    invalid_u_id = 1000
    response1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id'], invalid_u_id]
    })

    assert response1.status_code == 400

# InputError: Duplicate UIds
def test_duplicate_owner(user_1):
    response1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_1['auth_user_id']]
    })

    assert response1.status_code == 400

# InputError: Duplicate UIds
def test_duplicate_uid(user_1, user_2):
    response1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id'], user_2['auth_user_id']]
    })
    assert response1.status_code == 400

############################ TEST LISTING DM ############################

# Test empty DM list
def test_not_in_dm(user_1, user_2, user_3):
    requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    response2 = requests.get(f"{url}dm/list/v1", params = {'token': user_3['token']})
    not_in_dm = response2.json()
    assert not_in_dm == {'dms': []}

# Test user in 2 DMs
def test_2_dm_list(user_1, user_2, user_3):

    # Create 2 DMs
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_3['auth_user_id']]
    })
    dm_2 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id'], user_3['auth_user_id']]
    })
    dm_1_info = dm_1.json()
    dm_2_info = dm_2.json()

    # Check return of all DMs that user 1 is in
    response3 = requests.get(f"{url}dm/list/v1", params = {'token': user_1['token']})
    list_2_dm = response3.json()
    expected_response = {
        'dms': [{'dm_id': dm_1_info['dm_id'], 'name': 'userfirst, userthird'},
                {'dm_id': dm_2_info['dm_id'], 'name': 'userfirst, usersecond, userthird',}
        ]}
    assert list_2_dm == expected_response
    
############################ TEST REMOVE DM ############################

# AccessError when:      
# dm_id is valid and the authorised user is no longer in the DM
def test_dm_remove(user_1, user_2):
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    dm_1_info = dm_1.json()

    # User leaves
    requests.post(f"{url}dm/leave/v1", json={
        "token": user_1['token'],
        "dm_id": dm_1_info['dm_id'],
    })

    # Removed user cannot user remove
    response4 = requests.delete(f"{url}dm/remove/v1", json={
        "token": user_1['token'],
        "dm_id": dm_1_info['dm_id'],
    })
    assert response4.status_code == 403


# InputError when: dm_id does not refer to a valid DM
def test_dm_remove_nonvalid_dmid(user_1, user_2):
    invalid_dmid = 1000
    requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    response5 = requests.delete(f"{url}dm/remove/v1", json={
        "token": user_1['token'],
        "dm_id": invalid_dmid,
    })
    assert response5.status_code == 400

# AccessError when: dm_id is valid and the authorised user is not the original DM creator
def test_dm_remove_nonvalid_creator(user_1, user_2):        
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    dm_1_info = dm_1.json()
    response6 = requests.delete(f"{url}dm/remove/v1", json={
        "token": user_2['token'],
        "dm_id": dm_1_info['dm_id'],
    })
    assert response6.status_code == 403

# Valid case for removing someone from DM
def test_dm_remove_valid(user_1, user_2):

    # Create DM
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    dm_1 = response.json()['dm_id']

    # Remove DM entirely
    requests.delete(f"{url}dm/remove/v1", json={
        "token": user_1['token'],
        "dm_id": dm_1,
    })

    # Cannot access invalid DM when it no longer exists
    response = requests.get(f"{url}dm/details/v1", {'token': user_1['token'], 'dm_id': dm_1})
    assert response.status_code == 400

############################ TEST DM DETAILS ############################

# Test details for 2 person DM
def test_dm_details(user_1, user_2):

    # Create DM
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    dm_1_info = dm_1.json()

    # Both users call DM details
    response7 = requests.get(
        f"{url}dm/details/v1", 
        params = {'token': user_1['token'], 'dm_id': dm_1_info['dm_id']}
    )
    response8 = requests.get(
        f"{url}dm/details/v1", 
        params = {'token': user_2['token'], 'dm_id': dm_1_info['dm_id']}
    )

    # Both users should be returned same output
    required_output = { 
        'name': 'userfirst, usersecond',
        'members': [{
            'u_id': user_1['auth_user_id'],
            'name_first': 'User',
            'name_last': "First",
            'email': "email1@gmail.com",
            'handle_str': 'userfirst',
            'profile_img_url': f'{url}profileAvatar/default'
        }, {
            'u_id': user_2['auth_user_id'],
            'name_first': 'User',
            'name_last': "Second",
            'email': "email2@gmail.com",
            'handle_str': 'usersecond',
            'profile_img_url': f'{url}profileAvatar/default'
        }
        ],
    }
    assert response7.json() == required_output
    assert response8.json() == required_output

# InputError when: dm_id does not refer to a valid DM
def test_dm_details_nonvalid_dmid(user_1, user_2):
    wrong_dm_id = 10000
    requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    
    response9 = requests.get(
        f"{url}dm/details/v1", 
        params = {'token': user_1['token'], 'dm_id': wrong_dm_id}
    )

    assert response9.status_code == 400
    
# AccessError when: dm_id is valid and the authorised user is not a member of the DM
def test_dm_details_nonvalid_member(user_1, user_2, user_3):
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })

    dm_1_info = dm_1.json()

    response10 = requests.get(
        f"{url}dm/details/v1", 
        params = {'token': user_3['token'], 'dm_id': dm_1_info['dm_id']}
    )

    assert response10.status_code == 403

############################ TEST DM LEAVE ############################

# Test valid DM leave
def test_dm_leave(user_1, user_2):

    # Create DM
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    dm_1_info = dm_1.json()

    # User 2 leaves DM
    requests.post(f"{url}dm/leave/v1", json={
        "token": user_2['token'],
        "dm_id": dm_1_info['dm_id'],
    })

    # Get DM details
    response11 = requests.get(
        f"{url}dm/details/v1", 
        params = {'token': user_1['token'], 'dm_id': dm_1_info['dm_id']}
    )

    # Check only user 1 is in DM and DM name is still the same
    required_output = { 
        'name': 'userfirst, usersecond',
        'members': [{
            'u_id': user_1['auth_user_id'],
            'name_first': 'User',
            'name_last': "First",
            'email': "email1@gmail.com",
            'handle_str': 'userfirst',
            'profile_img_url': f'{url}profileAvatar/default'
        }
        ]
    }
    assert response11.json() == required_output


# InputError when: dm_id does not refer to a valid DM
def test_dm_leave_invalid_dm(user_1, user_2):
    das_da_wrong_number = 69
    requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })

    response12 = requests.post(f"{url}dm/leave/v1", json={
        "token": user_2['token'],
        "dm_id": das_da_wrong_number,
    })

    assert response12.status_code == 400


# AccessError when: dm_id is valid and the authorised user is not a member of the DM
def test_dm_leave_invalid_user(user_1, user_2, user_3):
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })

    dm_1_info = dm_1.json()

    response13 = requests.post(f"{url}dm/leave/v1", json={
        "token": user_3['token'],
        "dm_id": dm_1_info['dm_id'],
    })

    assert response13.status_code == 403

############################ TEST DM MESSAGES ############################

# InputError when any of: dm_id does not refer to a valid DM
def test_dm_messages_invalid_dmid(user_1, user_2):
    invalid_dm_id = 10000
    requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })

    response14 = requests.post(f"{url}message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": invalid_dm_id,
        "message": "I see you, I feel you",
    })
    
    assert response14.status_code == 400


# InputError when: length of message is less than 1 or over 1000 characters
def test_invalid_str(user_1, user_2):
    invalid_str = 'a'*1001
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })

    dm_1_info = dm_1.json()

    response15 = requests.post(f"{url}message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": dm_1_info['dm_id'],
        "message": invalid_str,
    })

    assert response15.status_code == 400


#  AccessError when: dm_id is valid and the authorised user is not a member of the DM
def test_dm_messages_invalid_id(user_1, user_2, user_3):
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })

    dm_1_info = dm_1.json()

    response16 = requests.post(f"{url}message/senddm/v1", json={
        "token": user_3['token'],
        "dm_id": dm_1_info['dm_id'],
        "message": "I put my hands up in the air some time",
    })

    assert response16.status_code == 403


# Test functionality of DM message return
def test_dm_messages(user_1, user_2):

    # Create DM
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })

    # Create DM dummy so we know it filters later
    dm_dummy = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": []
    })

    # Create Channel so we know messages from channels are filtered
    data_obj_1= {
        'token': user_1['token'],
        'name': 'FlandreScarlet', 
        'is_public': False,
    }
    c_dummy = requests.post(f'{url}channels/create/v2', json = data_obj_1)

    dm_1_info = dm_1.json()
    dm_dummy_info = dm_dummy.json()
    c_info = c_dummy.json()
    
    # Send message 1
    message_1 = {
        'token': user_1['token'],
        'dm_id': dm_1_info['dm_id'],
        'message': "Morris, Michael, Param and Roland",
        }
    response = requests.post(f'{url}message/senddm/v1', json = message_1)
    m_id1 = response.json()['message_id']

    # Send message 2
    message_2 = {
        'token': user_2['token'],
        'dm_id': dm_1_info['dm_id'],
        'message': "Anyone up for KFC?" 
        }
    response = requests.post(f'{url}message/senddm/v1', json = message_2)
    m_id2 = response.json()['message_id']

    # Check messages are stored with most recent message at head of list
    assert m_id1 < m_id2

    # Add dummy messages to test that message function filters other DMs
    message_dm_dummy = {
        'token': user_1['token'],
        'dm_id': dm_dummy_info['dm_id'],
        'message': "Once a jolly swagman" 
        }
    requests.post(f'{url}message/senddm/v1', json = message_dm_dummy)

    # Add dummy messages to test that message function filters channel messages
    message_ch_dummy = {
        'token': user_1['token'],
        'channel_id': c_info['channel_id'],
        'message': "Camped by a billabong" 
        }
    requests.post(f'{url}message/send/v1', json = message_ch_dummy)

    # Call message list function
    response = requests.get(f'{url}/dm/messages/v1', {
        'token': user_1['token'],
        'dm_id': dm_1_info['dm_id'],
        'start': 0
    })

    # Test return -1 when reach the end, order of returned list of messages
    assert response.json()['end'] == -1
    assert response.json()['messages'][0]['message'] == 'Anyone up for KFC?'
    assert response.json()['messages'][0]['u_id'] == user_2['auth_user_id']
    assert response.json()['messages'][1]['message'] == 'Morris, Michael, Param and Roland'

    # Test return start + 50 for end when not reach the end
    i = 0
    while i < 52:
        requests.post(f'{url}/message/senddm/v1', json = message_2)
        i += 1
    response = requests.get(f'{url}/dm/messages/v1', {
        'token': user_1['token'],
        'dm_id': dm_1_info['dm_id'],
        'start': 3
    })
    assert response.json()['end'] == 53


# Test invalid cases of messaging in DM
def test_invalid_dm_message(user_1, user_2, user_3):

    # Create DM
    dm_1 = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })

    dm_1_info = dm_1.json()

    # InputError: Test start greater than total dm messages
    response = requests.get(f'{url}/dm/messages/v1', {
        'token': user_1['token'],
        'dm_id': dm_1_info['dm_id'],
        'start': 10
    })
    assert response.status_code == 400

    # InputError: Invalid dm id for get messages
    response = requests.get(f'{url}/dm/messages/v1', {
        'token': user_1['token'],
        'dm_id': 88,
        'start': 0
    })
    assert response.status_code == 400

    # AccessError: User not in dm and try to get messages
    response = requests.get(f'{url}/dm/messages/v1', {
        'token': user_3['token'],
        'dm_id': dm_1_info['dm_id'],
        'start': 0
    })
    assert response.status_code == 403

# Test editing message in DM
def test_dm_edit(user_1, user_2, user_3):

    # Create DM with 3 members
    response = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id'], user_3['auth_user_id']]
    })
    dm = response.json()

    # Send message to DM
    message_1 = {
        'token': user_2['token'],
        'dm_id': dm['dm_id'],
        'message': "Morris, Michael, Param and Roland",
    }
    response = requests.post(f'{url}message/senddm/v1', json = message_1)
    m_id1 = response.json()['message_id']
    
    # DM owner edit messages
    edit_message = {
        'token': user_1['token'],
        'message_id': m_id1,
        'message': 'CS',
    }
    requests.put(f'{url}message/edit/v1', json = edit_message)
    response = requests.get(f'{url}dm/messages/v1', {
        'token': user_1['token'],
        'dm_id': dm['dm_id'],
        'start': 0
    })
    assert response.json()['messages'][0]['message'] == 'CS'

    # Message creator edit messages  
    edit_message = {
        'token': user_2['token'],
        'message_id': m_id1,
        'message': 'POIPOIPOI',
    }
    requests.put(f'{url}message/edit/v1', json = edit_message)
    response = requests.get(f'{url}dm/messages/v1', {
        'token': user_1['token'],
        'dm_id': dm['dm_id'],
        'start': 0
    })
    assert response.json()['messages'][0]['message'] == 'POIPOIPOI'

    # AccessError: user_3 try to edit messages
    edit_message = {
        'token': user_3['token'],
        'message_id': m_id1,
        'message': 'xxxxxxxxxxx',
    }
    response = requests.put(f'{url}message/edit/v1', json = edit_message)
    response.status_code == 403