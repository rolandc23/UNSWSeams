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
def c_1(user_1):
    data_obj_1= {
        'token': user_1['token'],
        'name': 'FlandreScarlet', 
        'is_public': True,
    }
    c_id = requests.post(f'{url}channels/create/v2', json = data_obj_1).json()['channel_id']
    return [user_1, c_id]


@pytest.fixture
def c_2(user_2):
    data_obj_1 = {
    'token': user_2['token'],
    'name': 'vampire', 
    'is_public': True,
    }
    c_id = requests.post(f'{url}channels/create/v2', json = data_obj_1).json()['channel_id']

    return [user_2, c_id]


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

def test_users_stat_simple(user_1, user_2, user_3, c_1):

    c_id = c_1[1]

    requests.post(f"{url}channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": c_id
    })


    requests.post(f"{url}message/send/v2", json={
        "token": user_1['token'],
        "channel_id": c_id,
        "message": "PARAM"
    }
    ).json() 
    
    response = requests.get(f"{url}users/stats/v1", params={'token': user_1['token']})

    assert response.status_code == 200

    assert response.json()["workspace_stats"]['channels_exist'][-1]['num_channels_exist'] == 1
    assert response.json()["workspace_stats"]['dms_exist'][-1]['num_dms_exist'] == 0
    assert response.json()["workspace_stats"]['messages_exist'][-1]['num_messages_exist'] == 0
    assert response.json()["workspace_stats"]["utilization_rate"] == 2/3



def test_utilization_rate_1(user_1, user_2, user_3, c_1, c_2, dm_1):

    c1_id = c_1[1]
    c2_id = c_2[1]

    requests.post(f"{url}channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": c1_id
    })


    requests.post(f"{url}message/send/v2", json={
        "token": user_1['token'],
        "channel_id": c1_id,
        "message": "PARAM"
    })


    requests.post(f"{url}channel/join/v2", json={
        "token": user_3['token'],
        "channel_id": c2_id
    })

    response = requests.get(f"{url}users/stats/v1", params={'token': user_1['token']})

    assert response.status_code == 200

    assert response.json()["workspace_stats"]['channels_exist'][-1]['num_channels_exist'] == 2
    assert response.json()["workspace_stats"]['dms_exist'][-1]['num_dms_exist'] == 1
    assert response.json()["workspace_stats"]['messages_exist'][-1]['num_messages_exist'] == 1
    assert response.json()["workspace_stats"]["utilization_rate"] == 1

def test_utilization_rate_0(user_1, c_1):

    c_id = c_1[1]

    requests.post(f"{url}channel/leave/v1", json={
        "token": user_1['token'],
        "channel_id": c_id,
    })

    response = requests.get(f"{url}users/stats/v1", params={'token': user_1['token']})

    assert response.status_code == 200

    assert response.json()["workspace_stats"]['channels_exist'][-1]['num_channels_exist'] == 1
    assert response.json()["workspace_stats"]["utilization_rate"] == 0


def test_dm_remove(user_1, dm_1):

    dm_id = dm_1[3]

    response_1 = requests.get(f"{url}users/stats/v1", params={'token': user_1['token']})
    assert response_1.json()["workspace_stats"]['dms_exist'][-1]['num_dms_exist'] == 1

    requests.delete(f"{url}dm/remove/v1", json={
        "token": user_1['token'],
        "dm_id": dm_id,
    })

    response_2 = requests.get(f"{url}users/stats/v1", params={'token': user_1['token']})
    assert response_2.json()["workspace_stats"]['dms_exist'][-1]['num_dms_exist'] == 0


def test_message_remove(user_1, dm_1):

    m_id = dm_1[2]

    response_1 = requests.get(f"{url}users/stats/v1", params={'token': user_1['token']})
    assert response_1.json()["workspace_stats"]['messages_exist'][-1]['num_messages_exist'] == 1

    parameter = {
        'token': user_1['token'],
        'message_id': m_id,
    }
    requests.delete(f'{url}message/remove/v1', json = parameter)

    response_2 = requests.get(f"{url}users/stats/v1", params={'token': user_1['token']})
    assert response_2.json()["workspace_stats"]['messages_exist'][-1]['num_messages_exist'] == 0





