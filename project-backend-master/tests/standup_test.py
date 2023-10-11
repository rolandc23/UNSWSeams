from inspect import Parameter
import pytest, requests
from src.config import url
from datetime import datetime
import time

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
        'is_public': True,
    }
    m_id = requests.post(f'{url}channels/create/v2', json = data_obj_1).json()['channel_id']
    return [user_1, m_id]


@pytest.fixture
def c_2(user_2):
    data_obj_1 = {
    'token': user_2['token'],
    'name': 'vampire', 
    'is_public': True,
    }
    m_id = requests.post(f'{url}channels/create/v2', json = data_obj_1).json()['channel_id']

    return [user_2, m_id]

# InputError when any of:
#         channel_id does not refer to a valid channel
#         length is a negative integer
#         an active standup is currently running in the channel

# InputError channel_id does not refer to a valid channel
def test_invalid_channel(user_1):
    response = requests.post(f"{url}standup/start/v1", json={
        'token': user_1['token'],
        'channel_id': 100,
        'length': 100
    })

    assert response.status_code == 400

# InputError when standup is already active in a channel
def test_already_active(c_1):
    response_1 = requests.post(f"{url}standup/start/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'length': 2
    })

    assert response_1.status_code == 200

    response_2 = requests.post(f"{url}standup/start/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'length': 1
    })
    assert response_2.status_code == 400
    time.sleep(2)

    
# InputError when length is negative
def test_invalid_length(c_1):
    response = requests.post(f"{url}standup/start/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'length': -1
    })

    assert response.status_code == 400

# AccessError when user is not in channel
def test_not_in_channel(c_1, user_2):
    response = requests.post(f"{url}standup/start/v1", json={
        'token': user_2['token'],
        'channel_id': c_1[1],
        'length': 1
    })

    assert response.status_code == 403

    time.sleep(1)

# Test functionality of standup start is working
def test_standup_start_basic(c_1):

    response = requests.post(f"{url}standup/start/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'length': 1
    })

    assert response.status_code == 200

    standup = response.json()
    finish = int(datetime.now().timestamp()) + 1
    assert standup['time_finish'] == finish

    time.sleep(1)


############################################################

# InputError: channel_id does not refer to a valid channel
def test_active_invalid_cid(user_1):
    response = requests.get(f"{url}standup/active/v1", {
        'token': user_1['token'],
        'channel_id': 10
    })
    assert response.status_code == 400


# AccessError: user is not in channel
def test_active_user_not_in(c_1, user_2):
    response = requests.get(f"{url}standup/active/v1", {
        'token': user_2['token'],
        'channel_id': c_1[1],
    })
    assert response.status_code == 403


# Test functionality of standup active is working as intended
def test_active_behaviour(c_1):
    
    token1 = c_1[0]['token']
    c_id = c_1[1]

    # Test none are active initially
    response_1 = requests.get(f"{url}standup/active/v1", {
        'token': token1,
        'channel_id': c_id,
    })
    assert response_1.status_code == 200
    assert response_1.json() == {'is_active': False, 'time_finish': None}

    # Test standup becomes active after creating one
    time_check = requests.post(f"{url}standup/start/v1", json={
        'token': token1,
        'channel_id': c_id,
        'length': 2
    }).json()

    time.sleep(1)

    response_2 = requests.get(f"{url}standup/active/v1", {
        'token': token1,
        'channel_id': c_id,
    })

    assert response_2.status_code == 200
    assert response_2.json() == {
        'is_active': True, 
        'time_finish': time_check['time_finish']
    }

    # Test standup becomes inactive after time_finish expires
    time.sleep(1)
    response_3 = requests.get(f"{url}standup/active/v1", {
        'token': token1,
        'channel_id': c_id,
    })
    assert response_3.status_code == 200
    assert response_3.json() == {'is_active': False, 'time_finish': None}


def test_send_invalid_cid(user_1):
    response = requests.post(f"{url}standup/send/v1", json={
        'token': user_1['token'],
        'channel_id': 100,
        "message": "Hello"
    })

    assert response.status_code == 400


def test_send_invalid_msg(c_1):

    requests.post(f"{url}standup/start/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'length': 1
    })

    response = requests.post(f"{url}standup/send/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        "message": "H"*1001
    })

    assert response.status_code == 400
    time.sleep(1)


def test_send_inactive(c_1):

    requests.post(f"{url}standup/start/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'length': 1
    })

    time.sleep(2)

    response = requests.post(f"{url}standup/send/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        "message": "My name is Jeff"
    })

    assert response.status_code == 400


def test_send_invalid_user(c_1, user_2):
    requests.post(f"{url}standup/start/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'length': 1
    })

    response = requests.post(f"{url}standup/send/v1", json={
        'token': user_2['token'],
        'channel_id': c_1[1],
        "message": "Geez My BAD"
    })

    assert response.status_code == 403
    time.sleep(1)


def test_send_one_message(c_1):
    
    requests.post(f"{url}standup/start/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'length': 1
    })

    response = requests.post(f"{url}standup/send/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        "message": "Hi"
    })

    assert response.status_code == 200

    check_no_messages = requests.get(f"{url}channel/messages/v2", params={
        "token": c_1[0]['token'],
        "channel_id": c_1[1],
        "start": 0
    }).json()['messages']

    assert len(check_no_messages) == 0

    time.sleep(2)

    check_messages = requests.get(f"{url}channel/messages/v2", params={
        "token": c_1[0]['token'],
        "channel_id": c_1[1],
        "start": 0
    }).json()['messages']

    assert len(check_messages) == 1
    assert check_messages[0]['message'] == 'userfirst: Hi'


def test_send_multiple_messages(c_1, user_2):
    
    requests.post(f"{url}standup/start/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'length': 1
    })

    requests.post(f'{url}channel/invite/v2', json = {
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'u_id': user_2['auth_user_id']
    })

    response_1 = requests.post(f"{url}standup/send/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        "message": "Hi"
    })

    assert response_1.status_code == 200

    response_2 = requests.post(f"{url}standup/send/v1", json={
        'token': user_2['token'],
        'channel_id': c_1[1],
        "message": "Bye"
    })

    assert response_2.status_code == 200

    time.sleep(2)

    check_messages = requests.get(f"{url}channel/messages/v2", params={
        "token": c_1[0]['token'],
        "channel_id": c_1[1],
        "start": 0
    }).json()['messages']

    assert len(check_messages) == 1
    assert check_messages[0]['message'] == 'userfirst: Hi\nusersecond: Bye'


def test_multiple_channel(c_1, c_2):
    
    # User 1 invite user 2 to channel 1
    requests.post(f'{url}channel/invite/v2', json = {
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'u_id': c_2[0]['auth_user_id']
    })
    # User 2 invite user 1 to channel 2
    requests.post(f'{url}channel/invite/v2', json = {
        'token': c_2[0]['token'],
        'channel_id': c_2[1],
        'u_id': c_1[0]['auth_user_id']
    })

    c_1_finish = requests.post(f"{url}standup/start/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'length': 2
    }).json()['time_finish']

    requests.post(f"{url}standup/start/v1", json={
        'token': c_2[0]['token'],
        'channel_id': c_2[1],
        'length': 1
    })

    response_1 = requests.post(f"{url}standup/send/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        "message": "Hi"
    })

    assert response_1.status_code == 200

    response_2 = requests.post(f"{url}standup/send/v1", json={
        'token': c_2[0]['token'],
        'channel_id': c_2[1],
        "message": "Bye"
    })

    assert response_2.status_code == 200

    time.sleep(1)
    check_messages_2 = requests.get(f"{url}channel/messages/v2", params={
        "token": c_2[0]['token'],
        "channel_id": c_2[1],
        "start": 0
    }).json()['messages']

    assert len(check_messages_2) == 1
    assert check_messages_2[0]['message'] == 'usersecond: Bye'

    resp = requests.get(f"{url}standup/active/v1", {
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
    })

    assert resp.status_code == 200
    assert resp.json() == {
        'is_active': True, 
        'time_finish': c_1_finish
    }

    time.sleep(1)
    check_messages_1 = requests.get(f"{url}channel/messages/v2", params={
        "token": c_1[0]['token'],
        "channel_id": c_1[1],
        "start": 0
    }).json()['messages']

    assert len(check_messages_1) == 1
    assert check_messages_1[0]['message'] == 'userfirst: Hi'




# Check message send in standup won't tagging user
def test_standup_msg_not_tagging(c_1,user_2):
    
    requests.post(f"{url}standup/start/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'length': 2
    })
    requests.post(f"{url}standup/send/v1", json={
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        "message": "@userfirst. NO TAGGING"
    })

    # User 2 join channel 1
    requests.post(f'{url}channel/join/v2', json = {
        'token': user_2['token'],
        'channel_id': c_1[1]
    })
    requests.post(f"{url}standup/send/v1", json={
        'token': user_2['token'],
        'channel_id': c_1[1],
        "message": "@userfirst. NO TAGGING"
    })
    time.sleep(2)
    resp = requests.get(f'{url}notifications/get/v1', {'token': c_1[0]['token']}).json()
    assert resp['notifications'] == []
    