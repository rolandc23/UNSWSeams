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
    data_obj= {
        'token': user_1['token'],
        'name': 'FlandreScarlet', 
        'is_public': True,
    }
    c_id = requests.post(f'{url}channels/create/v2', json = data_obj).json()['channel_id']
    message = {
        'token': user_1['token'],
        'channel_id': c_id,
        'message': 'Hello there!',
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
        'message': 'Sup dawgs',
    }
    m_id = requests.post(f'{url}message/send/v1', json = message).json()['message_id']
    return [user_2, c_id, m_id]


@pytest.fixture
def dm_1(user_1, user_2):
    data_obj = {
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    }
    dm_id = requests.post(f"{url}dm/create/v1", json=data_obj).json()['dm_id']
    message = {
        'token': user_1['token'],
        'dm_id': dm_id,
        'message': 'May the force be with you',
    }
    m_id = requests.post(f'{url}message/senddm/v1', json = message).json()['message_id']
    return [user_1, user_2, dm_id, m_id]


# Check user 1 can pin a message in channels/dms they are in
def test_valid_pin_unpin(user_1, c_1, dm_1):

    requests.post(f'{url}message/pin/v1', json={'token': user_1['token'], 'message_id': 0})
    response0 = requests.get(f'{url}channel/messages/v2', {
        'token': user_1['token'],
        'channel_id': c_1[1],
        'start': 0
    })
    assert response0.status_code == 200
    assert response0.json()['messages'][0]['is_pinned'] == True

    requests.post(f'{url}message/unpin/v1', json={'token': user_1['token'], 'message_id': 0})  
    response1 = requests.get(f'{url}channel/messages/v2', {
        'token': user_1['token'],
        'channel_id': c_1[1],
        'start': 0
    })
    assert response1.status_code == 200
    assert response1.json()['messages'][0]['is_pinned'] == False
    
    requests.post(f'{url}message/pin/v1', json={'token': user_1['token'], 'message_id': 1})
    response2 = requests.get(f'{url}dm/messages/v1', {
        'token': user_1['token'],
        'dm_id': dm_1[2],
        'start': 0
    })
    assert response2.status_code == 200
    assert response2.json()['messages'][0]['is_pinned'] == True

    requests.post(f'{url}message/unpin/v1', json={'token': user_1['token'], 'message_id': 1})
    response3 = requests.get(f'{url}dm/messages/v1', {
        'token': user_1['token'],
        'dm_id': dm_1[2],
        'start': 0
    })
    assert response3.status_code == 200
    assert response3.json()['messages'][0]['is_pinned'] == False


# pin the pinned msg again
def test_double_pin(c_1):
    resp = requests.post(f'{url}message/pin/v1', json={'token': c_1[0]['token'], 'message_id': 0})
    assert resp.status_code == 200
    resp = requests.post(f'{url}message/pin/v1', json={'token': c_1[0]['token'], 'message_id': 0})
    assert resp.status_code == 400


def test_unpin_invalid(c_1):
    resp = requests.post(f'{url}message/unpin/v1', json={'token': c_1[0]['token'], 'message_id': 0})
    assert resp.status_code == 400


def test_ch_pin_perm(c_1, user_2):

    # Not a member of channel 1
    resp = requests.post(f'{url}message/unpin/v1', json={'token': user_2['token'], 'message_id': c_1[1]})
    assert resp.status_code == 400
    # user_2 join channel 1 but do not have perm in channel 1
    requests.post(f'{url}channel/join/v2', json = {
        'token': user_2['token'],
        'channel_id': c_1[2]
    })
    resp = requests.post(f'{url}message/unpin/v1', json={'token': user_2['token'], 'message_id': c_1[1]})
    assert resp.status_code == 403
    # Set user_2 to seams owner
    requests.post(f'{url}admin/userpermission/change/v1', json={
        'token': c_1[0]['token'],
        'u_id': user_2['auth_user_id'],
        'permission_id': 1}
    )
    resp = requests.post(f'{url}message/pin/v1', json={'token': user_2['token'], 'message_id': c_1[1]})
    assert resp.status_code == 200
    resp = requests.post(f'{url}message/unpin/v1', json={'token': user_2['token'], 'message_id': c_1[1]})
    assert resp.status_code == 200


def test_dm_pin_perm(dm_1):
    resp = requests.post(f'{url}message/unpin/v1', json={'token': dm_1[1]['token'], 'message_id': dm_1[3]})
    assert resp.status_code == 403
    # Set user_2 to seams owner
    requests.post(f'{url}admin/userpermission/change/v1', json={
        'token': dm_1[0]['token'],
        'u_id': dm_1[1]['auth_user_id'],
        'permission_id': 1}
    )
    resp = requests.post(f'{url}message/unpin/v1', json={'token': dm_1[1]['token'], 'message_id': dm_1[3]})
    assert resp.status_code == 403

    
