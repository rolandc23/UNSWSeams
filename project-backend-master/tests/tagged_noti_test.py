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
def c_1(user_1):
    data_obj_1= {
        'token': user_1['token'],
        'name': 'FlandreScarlet', 
        'is_public': True,
    }
    response = requests.post(f'{url}channels/create/v2', json = data_obj_1).json()
    var1 = [user_1,response]
    return var1

@pytest.fixture
def dm_1(user_1, user_2):
    response = requests.post(f'{url}dm/create/v1', json={
        'token': user_1['token'],
        'u_ids': [user_2['auth_user_id']]
    }).json()
    return_list = [user_1,user_2,response]
    return return_list

def test_message_tagged_send_noti(c_1):
    
    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    message_1 = {
        'token': token1,
        'channel_id': c_id1,
        'message': '@userfirst=-=OHHHHHHH',
    }
    i = 0
    while i < 22:
        requests.post(f'{url}message/send/v1', json = message_1)
        i += 1
    response = requests.get(f'{url}notifications/get/v1', {'token': token1}).json()
    assert len(response['notifications']) == 20
    assert response['notifications'][0] == {
        'channel_id': c_id1,
        'dm_id': -1,
        'notification_message': 'userfirst tagged you in FlandreScarlet: @userfirst=-=OHHHHHH'
    }


def test_message_mulit_same_tagged(c_1):
    
    token1 = c_1[0]['token']
    c_id1 = c_1[1]['channel_id']
    message_1 = {
        'token': token1,
        'channel_id': c_id1,
        'message': '@userfirst@userfirst',
    }
    requests.post(f'{url}message/send/v1', json = message_1)

    response = requests.get(f'{url}notifications/get/v1', {'token': token1}).json()
    assert len(response['notifications']) == 1
    assert response['notifications'][0] == {
        'channel_id': c_id1,
        'dm_id': -1,
        'notification_message': 'userfirst tagged you in FlandreScarlet: @userfirst@userfirst'
    }


def test_tag_no_noti(c_1, user_2):
    token1 = c_1[0]['token']
    token2 = user_2['token']


    c_id1 = c_1[1]['channel_id']
    message_1 = {
        'token': token1,
        'channel_id': c_id1,
        'message': '@usersecond@usersecond',
    }
    requests.post(f'{url}message/send/v1', json = message_1)

    response = requests.get(f'{url}notifications/get/v1', {'token': token2}).json()
    assert len(response['notifications']) == 0


def test_tag_left_channel(c_1, user_2):
    
    token1 = c_1[0]['token']
    token2 = user_2['token']
    c_id1 = c_1[1]['channel_id']
    
    # User 2 join channel 1
    requests.post(f'{url}channel/join/v2', json = {
        'token': token2,
        'channel_id': c_id1
    })
    # User 1 send message to @user2
    message_1 = {
        'token': token1,
        'channel_id': c_id1,
        'message': '@usersecond@usersecond',
    }
    requests.post(f'{url}message/send/v1', json = message_1)
    # User 2 check notifications
    response = requests.get(f'{url}notifications/get/v1', {'token': token2}).json()
    assert len(response['notifications']) == 1
    assert response['notifications'][0] == {
        'channel_id': c_id1,
        'dm_id': -1,
        'notification_message': 'userfirst tagged you in FlandreScarlet: @usersecond@userseco'
    }

    # User 2 leaves channel 1
    requests.post(f'{url}channel/leave/v1', json = {
        'token': token2,
        'channel_id': c_id1
    })
    # User 1 tried to @user2 again
    message_1 = {
        'token': token1,
        'channel_id': c_id1,
        'message': '@usersecond@usersecond',
    }
    requests.post(f'{url}message/send/v1', json = message_1)
    # User 2 check notifications
    response = requests.get(f'{url}notifications/get/v1', {'token': token2}).json()
    assert len(response['notifications']) == 1


def test_tag_left_dm(dm_1):

    token1 = dm_1[0]['token']
    token2 = dm_1[1]['token']
    dm_id1 = dm_1[2]['dm_id']
    # User 1 send message to @user2
    message_dm = {
        'token': token1,
        'dm_id': dm_id1,
        'message': '@usersecond@usersecond' 
    }
    requests.post(f'{url}message/senddm/v1', json = message_dm)

    # User 2 check notifications
    response = requests.get(f'{url}notifications/get/v1', {'token': token2}).json()
    assert len(response['notifications']) == 2
    assert response['notifications'][1] == {
        'channel_id': -1,
        'dm_id': dm_id1,
        'notification_message': 'userfirst added you to userfirst, usersecond'
    }
    assert response['notifications'][0] == {
        'channel_id': -1,
        'dm_id': dm_id1,
        'notification_message': 'userfirst tagged you in userfirst, usersecond: @usersecond@userseco'
    }
    # User 1 send message to @user2 and @Invalidehandle
    message_dm = {
        'token': token1,
        'dm_id': dm_id1,
        'message': '@usersecond@invalid' 
    }
    requests.post(f'{url}message/senddm/v1', json = message_dm)
    response = requests.get(f'{url}notifications/get/v1', {'token': token2}).json()
    assert response['notifications'][0] == {
        'channel_id': -1,
        'dm_id': dm_id1,
        'notification_message': 'userfirst tagged you in userfirst, usersecond: @usersecond@invalid'
    }
  
    # User 2 leaves dm
    requests.post(f"{url}dm/leave/v1", json={
        "token": token2,
        "dm_id": dm_id1,
    })
    # User 1 send message to @user2
    message_dm = {
        'token': token1,
        'dm_id': dm_id1,
        'message': '@usersecond@usersecond' 
    }
    requests.post(f'{url}message/senddm/v1', json = message_dm)
    # User 2 check notifications
    response = requests.get(f'{url}notifications/get/v1', {'token': token2}).json()
    assert len(response['notifications']) == 3