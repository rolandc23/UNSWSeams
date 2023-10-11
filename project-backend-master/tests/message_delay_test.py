import pytest, requests
from datetime import datetime
import time
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
    return [user_1, user_2, c_id]

@pytest.fixture
def dm_1(user_1, user_2):
    dm_id = requests.post(f'{url}dm/create/v1', json={
        'token': user_1['token'],
        'u_ids': [user_2['auth_user_id']]
    }).json()['dm_id']
    return [user_1, user_2, dm_id]

def test_ch_invalid_timestamp(c_1):
    parameter = {
        'token': c_1[0]['token'],
        'channel_id': c_1[2],
        'message': 'This is invalid',
        'time_sent': 1648987857,
    }
    resp = requests.post(f'{url}message/sendlater/v1', json = parameter)
    assert resp.status_code == 400

def test_ch_invalid_cid(c_1):
    parameter = {
        'token': c_1[0]['token'],
        'channel_id': 7,
        'message': 'This is invalid',
        'time_sent': 1649160657,
    }
    resp = requests.post(f'{url}message/sendlater/v1', json = parameter)
    assert resp.status_code == 400

def test_ch_invalid_message(c_1):
    parameter = {
        'token': c_1[0]['token'],
        'channel_id': c_1[2],
        'message': 'N'*1001,
        'time_sent': 1649160657,
    }
    resp = requests.post(f'{url}message/sendlater/v1', json = parameter)
    assert resp.status_code == 400


def test_dm_invalid_timestamp(dm_1):
    parameter = {
        'token': dm_1[0]['token'],
        'dm_id': dm_1[2],
        'message': 'This is invalid',
        'time_sent': 1648987857,
    }
    resp = requests.post(f'{url}message/sendlaterdm/v1', json = parameter)
    assert resp.status_code == 400 

def test_dm_invalid_dmid(dm_1):
    parameter = {
        'token': dm_1[0]['token'],
        'dm_id': 7,
        'message': 'This is invalid',
        'time_sent': 1649160657,
    }
    resp = requests.post(f'{url}message/sendlaterdm/v1', json = parameter)
    assert resp.status_code == 400 

def test_dm_invalid_message(dm_1):
    parameter = {
        'token': dm_1[0]['token'],
        'dm_id': dm_1[2],
        'message': 'Q'*1001,
        'time_sent': 1649160657,
    }
    resp = requests.post(f'{url}message/sendlaterdm/v1', json = parameter)
    assert resp.status_code == 400

def test_ch_invalid_access(c_1):
    # User 2 leaves channel 1
    requests.post(f'{url}channel/leave/v1', json = {
        'token': c_1[1]['token'],
        'channel_id': c_1[2]
    })
    parameter = {
        'token': c_1[1]['token'],
        'channel_id': c_1[2],
        'message': 'N',
        'time_sent': 1649160657,
    }
    resp = requests.post(f'{url}message/sendlater/v1', json = parameter)
    assert resp.status_code == 403

def test_dm_invalid_access(dm_1):
    # User 2 leaves DM
    requests.post(f"{url}dm/leave/v1", json={
        "token": dm_1[1]['token'],
        "dm_id": dm_1[2],
    })
    parameter = {
        'token': dm_1[1]['token'],
        'dm_id': dm_1[2],
        'message': 'Q',
        'time_sent': 1649160657,
    }
    resp = requests.post(f'{url}message/sendlaterdm/v1', json = parameter)
    assert resp.status_code == 403

def test_ch_valid_delay(c_1):
    print(c_1)
    # First dealy message
    tmp_time = int(datetime.now().timestamp()) + 1
    parameter = {
        'token': c_1[0]['token'],
        'channel_id': c_1[2],
        'message': '@usersecond',
        'time_sent': tmp_time,
    }
    requests.post(f'{url}message/sendlater/v1', json = parameter)
    
    # Second delay message
    tmp_time = int(datetime.now().timestamp()) + 6
    parameter = {
        'token': c_1[1]['token'],
        'channel_id': c_1[2],
        'message': '@usersecond. GG',
        'time_sent': tmp_time,
    }
    requests.post(f'{url}message/sendlater/v1', json = parameter)
    
    # no channel message now
    response = requests.get(f'{url}channel/messages/v2', {
        'token': c_1[0]['token'],
        'channel_id': c_1[2],
        'start': 0
    }).json()['messages']
    assert response == []
    # Check user 2 should have no notification
    response = requests.get(f'{url}notifications/get/v1', {'token': c_1[1]['token']}).json()
    assert response['notifications'] == []
    
    # let pytest sleep 1 sec to recieve first message
    time.sleep(1)
    response = requests.get(f'{url}channel/messages/v2', {
        'token': c_1[0]['token'],
        'channel_id': c_1[2],
        'start': 0
    }).json()['messages'][0]['message']
    assert response == '@usersecond'
    # Check user 2 should have notification
    response = requests.get(f'{url}notifications/get/v1', {'token': c_1[1]['token']}).json()
    assert response['notifications'] == [{
        'channel_id': c_1[2],
        'dm_id': -1,
        'notification_message': 'userfirst tagged you in FlandreScarlet: @usersecond'
    }]
    # let pytest sleep 6 sec to recieve second message
    time.sleep(6)
    response = requests.get(f'{url}channel/messages/v2', {
        'token': c_1[0]['token'],
        'channel_id': c_1[2],
        'start': 0
    }).json()['messages'][0]['message']
    assert response == '@usersecond. GG'
    # There should be two notifications for user2
    response = requests.get(f'{url}notifications/get/v1', {'token': c_1[1]['token']}).json()
    assert response['notifications'] == [{
        'channel_id': c_1[2],
        'dm_id': -1,
        'notification_message': 'usersecond tagged you in FlandreScarlet: @usersecond. GG'
    },{
        'channel_id': c_1[2],
        'dm_id': -1,
        'notification_message': 'userfirst tagged you in FlandreScarlet: @usersecond'
    }]


def test_dm_valid_delay(dm_1):
    tmp_time = int(datetime.now().timestamp()) + 1
    parameter = {
        'token': dm_1[1]['token'],
        'dm_id': dm_1[2],
        'message': 'dm valid',
        'time_sent': tmp_time,
    }
    requests.post(f'{url}message/sendlaterdm/v1', json = parameter)
    response = requests.get(f'{url}dm/messages/v1', {
        'token': dm_1[0]['token'],
        'dm_id': dm_1[2],
        'start': 0
    }).json()['messages']
    assert response == []
    time.sleep(1)
    response = requests.get(f'{url}dm/messages/v1', {
        'token': dm_1[0]['token'],
        'dm_id': dm_1[2],
        'start': 0
    }).json()['messages'][0]['message']
    assert response == 'dm valid'
