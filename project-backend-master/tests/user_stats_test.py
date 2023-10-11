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


def test_user_stat (user_1, user_2):

    response = requests.post(f"{url}channels/create/v2", json={
        "token": user_1['token'],
        "name": 'channel',
        "is_public": True
    })

    channel_1 = response.json()


    requests.post(f"{url}channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_1['channel_id']
    })

    
    response = requests.get(f"{url}user/stats/v1", params={'token': user_1['token']}).json()

    assert response["user_stats"]['channels_joined'][-1]['num_channels_joined'] == 1
    assert response["user_stats"]['dms_joined'][-1]['num_dms_joined'] == 0
    assert response["user_stats"]['messages_sent'][-1]['num_messages_sent'] == 0
    assert response["user_stats"]["involvement_rate"] == 1



def test_user_stat_multiple (user_1, user_2):

    channel_1 = requests.post(f"{url}channels/create/v2", json={
        "token": user_1['token'],
        "name": 'channel',
        "is_public": True}
    )

    channel_1 = channel_1.json()

    requests.post(f"{url}channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_1['channel_id']
    })

    requests.post(f"{url}message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_1['channel_id'],
        "message": "PARAM"
    })

    dm = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    }).json()

    requests.post(f"{url}message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": dm['dm_id'],
        "message": "PARAMPARAM"
    })
    
    response_1 = requests.get(f"{url}user/stats/v1", params={'token': user_1['token']}).json()

    assert response_1["user_stats"]['channels_joined'][-1]['num_channels_joined'] == 1
    assert response_1["user_stats"]['dms_joined'][-1]['num_dms_joined'] == 1
    assert response_1["user_stats"]['messages_sent'][-1]['num_messages_sent'] == 2
    assert response_1["user_stats"]["involvement_rate"] == 1

    response_2 = requests.get(f"{url}user/stats/v1", params={'token': user_2['token']}).json()

    assert response_2["user_stats"]['channels_joined'][-1]['num_channels_joined'] == 1
    assert response_2["user_stats"]['dms_joined'][-1]['num_dms_joined'] == 1
    assert response_2["user_stats"]['messages_sent'][-1]['num_messages_sent'] == 0
    assert response_2["user_stats"]["involvement_rate"] == 0.5

def test_channel_remove(user_1):

    channel_1 = requests.post(f"{url}channels/create/v2", json={
        "token": user_1['token'],
        "name": 'channel',
        "is_public": True}
    )

    channel_1 = channel_1.json()

    response_1 = requests.get(f"{url}user/stats/v1", params={'token': user_1['token']})

    assert response_1.status_code == 200
    assert response_1.json()["user_stats"]['channels_joined'][-1]['num_channels_joined'] == 1

    requests.post(f"{url}channel/leave/v1", json={
        "token": user_1['token'],
        "channel_id": channel_1['channel_id'],
    })

    response_2 = requests.get(f"{url}user/stats/v1", params={'token': user_1['token']})

    assert response_2.status_code == 200
    assert response_2.json()["user_stats"]['channels_joined'][-1]['num_channels_joined'] == 0


def test_zero_involvement(user_1):

    response = requests.get(f"{url}user/stats/v1", params={'token': user_1['token']})

    assert response.json()["user_stats"]['involvement_rate'] == 0

def test_involvement_greater_than_1(user_1):

    dm = requests.post(f"{url}dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": []
    }).json()

    m_id = requests.post(f"{url}message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": dm['dm_id'],
        "message": "PARAMPARAM"
    }).json()['message_id']

    requests.post(f"{url}message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": dm['dm_id'],
        "message": "Hectic Bruh"
    })

    parameter = {
        'token': user_1['token'],
        'message_id': m_id,
    }
    requests.delete(f'{url}message/remove/v1', json = parameter)

    response = requests.get(f"{url}user/stats/v1", params={'token': user_1['token']})

    assert response.json()["user_stats"]['involvement_rate'] == 1

