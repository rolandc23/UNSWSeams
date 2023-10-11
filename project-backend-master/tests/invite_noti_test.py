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
    requests.post(f'{url}channel/invite/v2', json = {
        'token': user_1['token'],
        'channel_id': c_id,
        'u_id': user_2['auth_user_id']
    })

    return [user_1, user_2, c_id]

@pytest.fixture
def dm_1(user_1, user_2):
    dm_id = requests.post(f'{url}dm/create/v1', json={
        'token': user_1['token'],
        'u_ids': [user_2['auth_user_id']]
    }).json()['dm_id']
   
    return [user_1, user_2, dm_id]


def test_channel_invi_noti(c_1):
    response = requests.get(f'{url}notifications/get/v1', {'token': c_1[1]['token']}).json()
    assert response['notifications'] == [{
        'channel_id': c_1[2],
        'dm_id': -1,
        'notification_message': 'userfirst added you to FlandreScarlet'
        }
    ]

def test_dm_create_noti(dm_1):
    response = requests.get(f'{url}notifications/get/v1', {'token': dm_1[1]['token']}).json()
    assert response['notifications'] == [{
        'channel_id': -1,
        'dm_id': dm_1[2],
        'notification_message': 'userfirst added you to userfirst, usersecond'
        }
    ]