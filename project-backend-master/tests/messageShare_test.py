from inspect import Parameter
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
def user_3():
    data_obj = {
        'email': 'email2@gmail.com', 
        'password': 'password2',
        'name_first': 'User', 
        'name_last': 'Third'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    return response.json()

@pytest.fixture
def user_4():
    data_obj = {
        'email': 'email3@gmail.com', 
        'password': 'password3',
        'name_first': 'User', 
        'name_last': 'Fourth'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    return response.json()

@pytest.fixture
def c_1(user_1):
    data_obj= {
    'token': user_1['token'],
    'name': 'FlandreScarlet', 
    'is_public': True,
    }
    c_id = requests.post(f'{url}channels/create/v2', json = data_obj).json()['channel_id']
    message = {
        'token': user_1['token'],
        'channel_id': c_id,
        'message': "夜に駆ける",
        }
    m_id = requests.post(f'{url}message/send/v1', json = message).json()['message_id']
    return [user_1, c_id, m_id]

@pytest.fixture
def c_2(user_2):
    data_obj = {
    'token': user_2['token'],
    'name': 'vampire', 
    'is_public': True,
    }
    c_id = requests.post(f'{url}channels/create/v2', json = data_obj).json()['channel_id']
    message = {
        'token': user_2['token'],
        'channel_id': c_id,
        'message': "One Last Kiss",
        }
    m_id = requests.post(f'{url}message/send/v1', json = message).json()['message_id']
    return [user_2, c_id, m_id]

@pytest.fixture
def dm_1(user_3, user_4):
    data_obj = {
        "token": user_3['token'],
        "u_ids": [user_4['auth_user_id']]
    }
    dm_id = requests.post(f"{url}dm/create/v1", json=data_obj).json()['dm_id']
    message = {
        'token': user_3['token'],
        'dm_id': dm_id,
        'message': "ずっとそばに",
        }
    m_id = requests.post(f'{url}message/senddm/v1', json = message).json()['message_id']

    return [user_3, user_4, dm_id, m_id]


def test_invalid_sharing(c_1, c_2, dm_1):
    
    # User 2 join channel 1
    requests.post(f'{url}channel/join/v2', json = {
        'token': c_2[0]['token'],
        'channel_id': c_1[1]
    })
    
    # Both channel_id/dm_id are -1
    parameter = {
        'token': c_2[0]['token'],
        'og_message_id': c_2[2],
        'message': 'By Utada Hikaru',
        'channel_id': -1,
        'dm_id': -1,
    }
    resp = requests.post(f'{url}message/share/v1', json = parameter)
    assert resp.status_code == 400
    
    # Invalid channel id
    parameter = {
        'token': c_2[0]['token'],
        'og_message_id': c_2[2],
        'message': 'By Utada Hikaru',
        'channel_id': 20,
        'dm_id': -1,
    }
    resp = requests.post(f'{url}message/share/v1',json = parameter)
    assert resp.status_code == 400
    
    # Invalid dm_id
    parameter = {
        'token': c_2[0]['token'],
        'og_message_id': c_2[2],
        'message': 'By Utada Hikaru',
        'channel_id': -1,
        'dm_id': 20,
    }
    resp = requests.post(f'{url}message/share/v1',json = parameter)
    assert resp.status_code == 400
    
    # Given both c_id and dm_id are valid. Is a valid use of HTTP end point
    parameter = {
        'token': c_2[0]['token'],
        'og_message_id': c_2[2],
        'message': 'By Utada Hikaru',
        'channel_id': c_1[1],
        'dm_id': dm_1[2],
    }
    resp = requests.post(f'{url}message/share/v1',json = parameter)
    assert resp.status_code == 400

    # optional message over-length
    parameter = {
        'token': c_2[0]['token'],
        'og_message_id': c_2[2],
        'message': '✟升天✟​'*250+'!',
        'channel_id': c_1[1],
        'dm_id': -1,
    }
    resp = requests.post(f'{url}message/share/v1',json = parameter)
    assert resp.status_code == 400

    # Share messages to channel not joined
    parameter = {
        'token': c_1[0]['token'],
        'og_message_id': c_1[2],
        'message': 'inertia',
        'channel_id': c_2[1],
        'dm_id': -1,
    }
    resp = requests.post(f'{url}message/share/v1',json = parameter)
    assert resp.status_code == 403
    
    # Share messages to dm not joined
    parameter = {
        'token': c_2[0]['token'],
        'og_message_id': c_2[2],
        'message': 'inertia',
        'channel_id': -1,
        'dm_id': dm_1[2],
    }
    resp = requests.post(f'{url}message/share/v1',json = parameter)
    assert resp.status_code == 403


def test_share_C2C(c_1, c_2):
    # User 2 join channel 1
    requests.post(f'{url}channel/join/v2', json = {
        'token': c_2[0]['token'],
        'channel_id': c_1[1]
    })
    parameter = {
        'token': c_2[0]['token'],
        'og_message_id': c_2[2],
        'message': 'By Utada Hikaru',
        'channel_id': c_1[1],
        'dm_id': -1,
    }
    shared_message = requests.post(f'{url}message/share/v1', json = parameter).json()['shared_message_id']
    response = requests.get(f'{url}channel/messages/v2', {
        'token': c_2[0]['token'],
        'channel_id': c_1[1],
        'start': 0
    }).json()['messages']
    assert response[0]['message_id'] == shared_message
    assert 'One Last Kiss' in response[0]['message']
    assert 'By Utada Hikaru' in response[0]['message']

def test_share_DM2C(c_1, dm_1):
    # User 3 join channel 1
    requests.post(f'{url}channel/join/v2', json = {
        'token': dm_1[0]['token'],
        'channel_id': c_1[1]
    })
    # User 3 share dm's message to channel 1
    parameter = {
        'token': dm_1[0]['token'],
        'og_message_id': dm_1[3],
        'message': 'By Cö Shu Nie',
        'channel_id': c_1[1],
        'dm_id': -1,
    }
    shared_message = requests.post(f'{url}message/share/v1', json = parameter).json()['shared_message_id']
    response = requests.get(f'{url}channel/messages/v2', {
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'start': 0
    }).json()['messages']
    assert response[0]['message_id'] == shared_message
    assert 'ずっとそばに' in response[0]['message']
    assert 'By Cö Shu Nie' in response[0]['message']
    # User 3 share channel 1's message to dm
    parameter = {
        'token': dm_1[0]['token'],
        'og_message_id': c_1[2],
        'message': 'By Yoasobi',
        'channel_id': -1,
        'dm_id': dm_1[2],
    }
    shared_message = requests.post(f'{url}message/share/v1', json = parameter).json()['shared_message_id']
    response = requests.get(f'{url}dm/messages/v1', {
        'token': dm_1[0]['token'],
        'dm_id': dm_1[2],
        'start': 0
    }).json()['messages']
    assert response[0]['message_id'] == shared_message
    assert '夜に駆ける' in response[0]['message']
    assert 'By Yoasobi' in response[0]['message']

def test_tag_share(c_1, c_2):
    # User 2 not in channel 1 yet. user 1 try to @user2
    message = {
        'token': c_1[0]['token'],
        'channel_id': c_1[1],
        'message': '@usersecond' 
    }
    m_id = requests.post(f'{url}message/send/v1', json = message).json()['message_id']
    response = requests.get(f'{url}notifications/get/v1', {'token': c_2[0]['token']}).json()
    assert response['notifications'] == []

    # User 2 join channel 1
    requests.post(f'{url}channel/join/v2', json = {
        'token': c_2[0]['token'],
        'channel_id': c_1[1]
    })

    parameter = {
        'token': c_2[0]['token'],
        'og_message_id': m_id,
        'message': '@usersecond',
        'channel_id': c_2[1],
        'dm_id': -1,
    }
    resp = requests.post(f'{url}message/share/v1', json = parameter)
    assert resp.status_code == 200
    response = requests.get(f'{url}notifications/get/v1', {'token': c_2[0]['token']}).json()
    assert response['notifications'] == [{
        'channel_id': c_2[1],
        'dm_id': -1,
        'notification_message': 'usersecond tagged you in vampire: @usersecond.@usersec'
    }]