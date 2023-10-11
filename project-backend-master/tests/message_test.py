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

############################ TEST SEND MESSAGES TO CHANNEL ############################

# The check of sending input correctly case was combined in channel/messages/v2
def test_invalid_send_messages(c_1, c_2):
    
    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    token2 = c_2[0]['token']
    
    # InputError: Send messaages to invalid channel
    message_1 = {
        'token': token1,
        'channel_id': 99,
        'message': "Morris, Michael, Param and Roland",
        }
    response = requests.post(f'{url}message/send/v1', json = message_1)
    assert response.status_code == 400

    # InputError: Send empty message
    message_2 = {
        'token': token1,
        'channel_id': c_id1,
        'message': "",
        }
    response = requests.post(f'{url}message/send/v1', json = message_2)
    assert response.status_code == 400

    # InputError: Send message too long
    message_3 = {
        'token': token1,
        'channel_id': c_id1,
        'message': "Q"*1001,
        }
    response = requests.post(f'{url}message/send/v1', json = message_3)
    assert response.status_code == 400

    # AccessError: Auth user not in channel sending message
    message_4 = {
        'token': token2,
        'channel_id': c_id1,
        'message': "EldenRing",
        }
    response = requests.post(f'{url}message/send/v1', json = message_4)
    assert response.status_code == 403

############################ TEST EDIT/REMOVE CHANNEL MESSAGES ############################

# Creator edits own message in channel
def test_edit_own_message(c_1):

    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    
    # Send message
    message_1 = {
        'token': token1,
        'channel_id': c_id1,
        'message': "Morris, Michael, Param and Roland",
        }
    response = requests.post(f'{url}message/send/v1', json = message_1)
    message_id_1 = response.json()['message_id']
    
    # Edit message
    edit_message = {
        'token': token1,
        'message_id': message_id_1,
        'message': 'CS3231',
    }
    requests.put(f'{url}message/edit/v1', json = edit_message)

    # Check message has been edited
    response = requests.get(f'{url}channel/messages/v2', {
        'token': token1,
        'channel_id': c_id1,
        'start': 0
    })
    assert response.json()['messages'][0]['message'] == 'CS3231'

    # Edit with '' empty string
    edit_message = {
        'token': token1,
        'message_id': message_id_1,
        'message': '',
    }
    requests.put(f'{url}message/edit/v1', json = edit_message)

    # Check message has been deleted
    response = requests.get(f'{url}channel/messages/v2', {
        'token': token1,
        'channel_id': c_id1,
        'start': 0
    })
    assert response.json()['messages'] == []
    

# Test owner perm user editing other's messages
def test_edit_other(c_1, c_2):

    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    token2 = c_2[0]['token']
    u_id2 = c_2[0]['auth_user_id']

    # User 1 invites user 2
    requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })

    # User 2 sends message 1
    message_1 = {
        'token': token2,
        'channel_id': c_id1,
        'message': "Morris, Michael, Param and Roland",
        }
    response = requests.post(f'{url}message/send/v1', json = message_1)
    message_id_1 = response.json()['message_id']
    
    # Channel owner edits message
    edit_message = {
        'token': token1,
        'message_id': message_id_1,
        'message': 'CS3231',
    }
    requests.put(f'{url}message/edit/v1', json = edit_message)

    # Check message has been edited
    response = requests.get(f'{url}channel/messages/v2', {
        'token': token1,
        'channel_id': c_id1,
        'start': 0
    })
    assert response.json()['messages'][0]['message'] == 'CS3231'

    # Make empty entry for message edit
    edit_message = {
        'token': token1,
        'message_id': message_id_1,
        'message': '',
    }
    requests.put(f'{url}message/edit/v1', json = edit_message)

    # Check message has been deleted
    response = requests.get(f'{url}channel/messages/v2', {
        'token': token1,
        'channel_id': c_id1,
        'start': 0
    })
    assert response.json()['messages'] == []


# Invalid cases of editing message
def test_invalid_edit_message(c_1, c_2):

    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    token2 = c_2[0]['token']
    u_id2 = c_2[0]['auth_user_id']
    
    # Send message
    message_1 = {
        'token': token1,
        'channel_id': c_id1,
        'message': "Morris, Michael, Param and Roland",
        }
    response = requests.post(f'{url}message/send/v1', json = message_1)
    message_id = response.json()['message_id']
    
    # InputError: Invalid message edit entry too long
    edit_message = {
        'token': token1,
        'message_id': message_id,
        'message': 'CS'*501,
    }
    response = requests.put(f'{url}message/edit/v1', json = edit_message)
    assert response.status_code == 400

    # InputError: Invalid message ID
    edit_message = {
        'token': token1,
        'message_id': 999,
        'message': 'C1112',
    }
    response = requests.put(f'{url}message/edit/v1', json = edit_message)
    assert response.status_code == 400
    
    # InputError: Editor is not member of channel of the message
    edit_message = {
        'token': token2,
        'message_id': message_id,
        'message': 'CS',
    }
    response = requests.put(f'{url}message/edit/v1', json = edit_message)
    assert response.status_code == 400

    # AccessError: Invite user 2 and check they still cannot edit
    requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })
    response = requests.put(f'{url}message/edit/v1', json = edit_message)
    assert response.status_code == 403


# Remove message valid case
def test_message_remove(c_1):

    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    
    # Send message to channel
    message_1 = {
        'token': token1,
        'channel_id': c_id1,
        'message': "Morris, Michael, Param and Roland",
        }
    response = requests.post(f'{url}message/send/v1', json = message_1)
    message_id = response.json()['message_id']
    
    # Delete message
    parameter = {
        'token': token1,
        'message_id': message_id,
    }
    requests.delete(f'{url}message/remove/v1', json = parameter)
    
    # Check message is deleted
    response = requests.get(f'{url}channel/messages/v2', {
        'token': token1,
        'channel_id': c_id1,
        'start': 0
    })
    assert response.json()['messages'] == []


# Invalid cases for removing messages
def test_invalid_message_remove(c_1, c_2):

    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    token2 = c_2[0]['token']
    u_id2 = c_2[0]['auth_user_id']
    
    # Send message 1
    message_1 = {
        'token': token1,
        'channel_id': c_id1,
        'message': "Morris, Michael, Param and Roland",
        }
    response = requests.post(f'{url}message/send/v1', json = message_1)
    message_id = response.json()['message_id']

    # InputError: Delete message with invalid message ID
    parameter = {
        'token': token1,
        'message_id': 999,
    }
    response = requests.delete(f'{url}message/remove/v1', json = parameter)
    assert response.status_code == 400
    
    # InputError: Remover is not in channel of message
    parameter = {
        'token': token2,
        'message_id': message_id,
    }
    response = requests.delete(f'{url}message/remove/v1', json = parameter)
    assert response.status_code == 400
    
    # AccessError: Invite user 2 and check that they still cannot remove message
    requests.post(f'{url}channel/invite/v2', json = {
        'token': token1,
        'channel_id': c_id1,
        'u_id': u_id2
    })
    response = requests.delete(f'{url}message/remove/v1', json = parameter)
    assert response.status_code == 403 