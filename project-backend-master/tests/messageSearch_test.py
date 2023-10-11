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
        'message': "Hello World",
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
        'message': "HEAVEN AND HELL",
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
        'message': 'Elephants in Africa',
    }
    m_id = requests.post(f'{url}message/senddm/v1', json = message).json()['message_id']
    return [user_1, user_2, dm_id, m_id]

# Check user 1 can get a list back from his own channel
def test_valid_search(user_1, c_1, dm_1):
    data_obj1 = {
        'token': user_1['token'], 
        'query_str': 'World'
    }
    response1 = requests.get(f'{url}search/v1', data_obj1)
    assert response1.status_code == 200
    assert response1.json()['messages'] == ['Hello World']

    response2 = requests.get(f'{url}search/v1', {
        'token': user_1['token'], 
        'query_str': 'h'}).json()
    assert 'Hello World' in response2['messages']
    assert 'Elephants in Africa' in response2['messages']

# Check that user 2 can't get a list from user 1's channel despite having a valid message in the channel
def test_user_search_permissions(user_1, user_2, c_1, c_2):

    response1 = requests.get(f'{url}search/v1', {'token': user_2['token'], 'query_str': 'Hell'}).json()
    assert response1['messages'] == ['HEAVEN AND HELL']

    # Add user to channel, then test again and should return a message list
    requests.post(f'{url}channel/join/v2', json = {
        'token': user_2['token'],
        'channel_id': c_1[1]
    })
    response2 = requests.get(f'{url}search/v1', {'token': user_2['token'], 'query_str': 'Hell'}).json()
    assert response2['messages'] == ['HEAVEN AND HELL', 'Hello World']

    # Remove user 1 from channel, then test again and should return nothing
    requests.post(f'{url}channel/leave/v1', json = {
        'token': user_1['token'],
        'channel_id': c_1[1]
    })
    response3 = requests.get(f'{url}search/v1', {'token': user_1['token'], 'query_str': 'Hello World'}).json()
    assert response3['messages'] == []

# Check user 1 returns an empty list with an non-existent substring input
def test_non_existent_search_query_substring(user_1):

    response = requests.get(f'{url}search/v1', {'token': user_1['token'], 'query_str': 'abc'}).json()
    assert response['messages'] == []

# Check that entering an empty query returns input error
def test_invalid_query_string_length(user_1):

    response1 = requests.get(f'{url}search/v1', {'token': user_1['token'], 'query_str': ''})
    assert response1.status_code == 400

    response2 = requests.get(f'{url}search/v1', {'token': user_1['token'], 'query_str': 'a'*1001})
    assert response2.status_code == 400
