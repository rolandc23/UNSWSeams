import pytest, requests
from src.config import url

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
def c_1(user_1,user_2):
    data_obj_1= {
        'token': user_1['token'],
        'name': 'FlandreScarlet', 
        'is_public': True,
    }
    c_id = requests.post(f'{url}channels/create/v2', json = data_obj_1).json()['channel_id']
    requests.post(f'{url}channel/join/v2', json = {
        'token': user_2['token'],
        'channel_id': c_id
    })
    message_1 = {
        'token': user_2['token'],
        'channel_id': c_id,
        'message': 'we_test_react_channel',
    }
    m_id = requests.post(f'{url}message/send/v1', json = message_1).json()['message_id']
    return [user_1, user_2, m_id, c_id]

@pytest.fixture
def dm_1(user_1, user_2):
    dm_id = requests.post(f'{url}dm/create/v1', json={
        'token': user_1['token'],
        'u_ids': [user_2['auth_user_id']]
    }).json()['dm_id']
    message_dm = {
        'token': user_2['token'],
        'dm_id': dm_id,
        'message': 'we_test_react_dm' 
    }
    m_id = requests.post(f'{url}message/senddm/v1', json = message_dm).json()['message_id']
    return [user_1, user_2, m_id, dm_id]


def test_react_channel_valid(c_1):
    expected_output = [{
        'channel_id': c_1[3],
        'dm_id': -1,
        'notification_message': 'userfirst reacted to your message in FlandreScarlet'
    },
    {
        'channel_id': c_1[3],
        'dm_id': -1,
        'notification_message': 'usersecond reacted to your message in FlandreScarlet'
    }]
    # User 2 react to self-message
    parameter = {
        'token': c_1[1]['token'],
        'message_id': c_1[2],
        'react_id': 1,
    }
    requests.post(f'{url}message/react/v1', json = parameter)

    # User 1 react to user 2's message
    parameter = {
        'token': c_1[0]['token'],
        'message_id': c_1[2],
        'react_id': 1,
    }
    requests.post(f'{url}message/react/v1', json = parameter)
    
    # User 2 check notification
    response = requests.get(f'{url}notifications/get/v1', {'token': c_1[1]['token']}).json()
    assert response['notifications'] == expected_output

    # User 2 left channel
    requests.post(f'{url}channel/leave/v1', json = {
        'token': c_1[1]['token'],
        'channel_id': c_1[3]
    })
    # User 1 unreact and react again. because user 2 left channel, user 2 won't get another notification.
    requests.post(f'{url}message/unreact/v1', json = parameter)
    requests.post(f'{url}message/react/v1', json = parameter)
    # User 2 check notification again
    response = requests.get(f'{url}notifications/get/v1', {'token': c_1[1]['token']}).json()
    assert response['notifications'] == expected_output

def test_react_dm_valid(dm_1):
    parameter = {
        'token': dm_1[0]['token'],
        'message_id': dm_1[2],
        'react_id': 1,
    }
    requests.post(f'{url}message/react/v1', json = parameter)
    response = requests.get(f'{url}notifications/get/v1', {'token': dm_1[1]['token']}).json()
    assert response['notifications'][0] == {
        'channel_id': -1,
        'dm_id': dm_1[3],
        'notification_message': 'userfirst reacted to your message in userfirst, usersecond'
    }
    # User 2 left DM
    requests.post(f"{url}dm/leave/v1", json={
        "token": dm_1[1]['token'],
        "dm_id": dm_1[3],
    })
    # User 1 unreact and react again. because user 2 left dm, user 2 won't get another notification.
    requests.post(f'{url}message/unreact/v1', json = parameter)
    requests.post(f'{url}message/react/v1', json = parameter)
    # User 2 check notification again
    response = requests.get(f'{url}notifications/get/v1', {'token': dm_1[1]['token']}).json()
    assert response['notifications'][0] == {
        'channel_id': -1,
        'dm_id': dm_1[3],
        'notification_message': 'userfirst reacted to your message in userfirst, usersecond'
    }

def test_unreact_channel(c_1):
    parameter = {
        'token': c_1[0]['token'],
        'message_id': c_1[2],
        'react_id': 1,
    }
    requests.post(f'{url}message/react/v1', json = parameter)
    # User 1 Call channel messages
    c_message = requests.get(f'{url}channel/messages/v2', {
        'token': c_1[0]['token'],
        'channel_id': c_1[2],
        'start': 0
    }).json()
    # User 1 got reacted as True
    assert c_message['messages'][0]['reacts'] == [{
        "react_id": 1, 
        "u_ids": [0],
        'is_this_user_reacted': True
    }]
    # User 2 Call channel messages
    c_message = requests.get(f'{url}channel/messages/v2', {
        'token': c_1[1]['token'],
        'channel_id': c_1[2],
        'start': 0
    }).json()
    # User 2 got reacted as False
    assert c_message['messages'][0]['reacts'] == [{
        "react_id": 1, 
        "u_ids": [0],
        'is_this_user_reacted': False
    }]
    # User 1 cancel react
    requests.post(f'{url}message/unreact/v1', json = parameter)
    # User 1 Call channel messages
    c_message = requests.get(f'{url}channel/messages/v2', {
        'token': c_1[0]['token'],
        'channel_id': c_1[2],
        'start': 0
    }).json()
    # User 1 got reacted as False
    assert c_message['messages'][0]['reacts'] == [{
        "react_id": 1, 
        "u_ids": [],
        'is_this_user_reacted': False
    }]

def test_unreact_dm(dm_1):
    parameter = {
        'token': dm_1[0]['token'],
        'message_id': dm_1[2],
        'react_id': 1,
    }
    requests.post(f'{url}message/react/v1', json = parameter)
    # User 1 Call dm messages
    dm_message = requests.get(f'{url}dm/messages/v1', {
        'token': dm_1[0]['token'],
        'dm_id': dm_1[2],
        'start': 0
    }).json()
    # User 1 got reacted as True
    assert dm_message['messages'][0]['reacts'] == [{
        "react_id": 1, 
        "u_ids": [0],
        'is_this_user_reacted': True
    }]
    # User 2 Call dm messages
    dm_message = requests.get(f'{url}dm/messages/v1', {
        'token': dm_1[1]['token'],
        'dm_id': dm_1[2],
        'start': 0
    }).json()
    # User 2 got reacted as False
    assert dm_message['messages'][0]['reacts'] == [{
        "react_id": 1, 
        "u_ids": [0],
        'is_this_user_reacted': False
    }]
    # User 1 cancel react
    requests.post(f'{url}message/unreact/v1', json = parameter)
    # User 1 Call dm messages
    dm_message = requests.get(f'{url}dm/messages/v1', {
        'token': dm_1[0]['token'],
        'dm_id': dm_1[2],
        'start': 0
    }).json()
    # User 1 got reacted as False
    assert dm_message['messages'][0]['reacts'] == [{
        "react_id": 1, 
        "u_ids": [],
        'is_this_user_reacted': False
    }]

def test_invalid_react(c_1):
    
    # Invalid message_id
    parameter = {
        'token': c_1[0]['token'],
        'message_id': 999,
        'react_id': 1,
    }
    response = requests.post(f'{url}message/react/v1', json = parameter)
    assert response.status_code == 400
    
    # Invalid react id
    parameter = {
        'token': c_1[0]['token'],
        'message_id': c_1[2],
        'react_id': 88,
    }
    response = requests.post(f'{url}message/react/v1', json = parameter)
    assert response.status_code == 400
    
    # already reacted
    parameter = {
        'token': c_1[0]['token'],
        'message_id': c_1[2],
        'react_id': 1,
    }
    requests.post(f'{url}message/react/v1', json = parameter)
    response = requests.post(f'{url}message/react/v1', json = parameter)
    assert response.status_code == 400
    
    # m_id is valid, but user not in that channel
    # User 2 leaves channel 1
    requests.post(f'{url}channel/leave/v1', json = {
        'token': c_1[1]['token'],
        'channel_id': c_1[3]
    })
    parameter = {
        'token': c_1[1]['token'],
        'message_id': c_1[2],
        'react_id': 1,
    }
    response = requests.post(f'{url}message/react/v1', json = parameter)
    assert response.status_code == 400

def test_invalid_ch_unreact(c_1):
    # Invalid message_id
    parameter = {
        'token': c_1[0]['token'],
        'message_id': 999,
        'react_id': 1,
    }
    response = requests.post(f'{url}message/unreact/v1', json = parameter)
    assert response.status_code == 400
    
    # Invalid react id
    parameter = {
        'token': c_1[0]['token'],
        'message_id': c_1[2],
        'react_id': 88,
    }
    response = requests.post(f'{url}message/unreact/v1', json = parameter)
    assert response.status_code == 400
    
    
    parameter = {
        'token': c_1[0]['token'],
        'message_id': c_1[2],
        'react_id': 1,
    }
    # No react even created
    response = requests.post(f'{url}message/unreact/v1', json = parameter)
    assert response.status_code == 400
    # test already unreacted
    requests.post(f'{url}message/react/v1', json = parameter)
    requests.post(f'{url}message/unreact/v1', json = parameter)
    response = requests.post(f'{url}message/unreact/v1', json = parameter)
    assert response.status_code == 400
    
    
    # User 2 didn't react to the message and tried to unreact it
    parameter = {
        'token': c_1[1]['token'],
        'message_id': c_1[2],
        'react_id': 1,
    }
    response = requests.post(f'{url}message/unreact/v1', json = parameter)
    assert response.status_code == 400
    response = requests.post(f'{url}message/react/v1', json = parameter)
    assert response.status_code == 200
    # User 2 leaves channel 1
    requests.post(f'{url}channel/leave/v1', json = {
        'token': c_1[1]['token'],
        'channel_id': c_1[3]
    })
    # m_id is valid, but user not in that channel
    response = requests.post(f'{url}message/unreact/v1', json = parameter)
    assert response.status_code == 400

def test_invalid_dm_unreact(dm_1):
    parameter = {
        'token': dm_1[1]['token'],
        'message_id': dm_1[2],
        'react_id': 1,
    }
    requests.post(f'{url}message/react/v1', json = parameter)
    # User 2 leaves dm
    requests.post(f"{url}dm/leave/v1", json={
        "token": dm_1[1]['token'],
        "dm_id": dm_1[3],
    })
    response = requests.post(f'{url}message/unreact/v1', json = parameter)
    assert response.status_code == 400
