import pytest
import requests
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

############################ TEST CHANNEL CREATE/INVALID ############################

# Check AccessError can be raised
def test_invalid_access():
    
    # Invalid access to create
    invalid_token = 'DADAM,LKLJMNBJHU2'
    response = requests.post(f'{url}channels/create/v2', json = {
        'token': invalid_token,
        'name': 'ERROR',
        'is_public': True,
        }
    )

    # Invalid access to list
    assert response.status_code == 403
    response = requests.get(f'{url}channels/list/v2', {
        'token': invalid_token,
        }
    )

    # Invalid access to listall
    assert response.status_code == 403        
    response = requests.get(f'{url}channels/listall/v2', {
        'token': invalid_token,
        }
    )
    assert response.status_code == 403
     

# InputError when: length of name is more than 20 characters
def test_name_long(user_1):
    token = user_1['token']
    response = requests.post(f'{url}channels/create/v2', json = {
        'token': token,
        'name': 'P' * 22,
        'is_public': True,
        }
    )
    assert response.status_code == 400


# InputError: length of name is less than 1 
def test_name_short(user_1):
    token = user_1['token']
    response = requests.post(f'{url}channels/create/v2', json = {
        'token': token,
        'name': '',
        'is_public': True,
        }
    )
    assert response.status_code == 400


# Check with two Errors, raise AccessError
def test_channels_create_errors():
    invalid_token = 'DADAM,LKLJMNBJHU2'
    requests.post(f'{url}channels/create/v2', json = {
        'token': invalid_token,
        'name': 'P' * 22,
        'is_public': True,
        }
    )

############################ TEST CHANNEL LIST/LISTALL ############################

# Test list and listall return
def test_list_listall(user_1, user_2):
    
    # Create a channel using user_1
    data_obj_1= {
    'token': user_1['token'],
    'name': 'FlandreScarlet', 
    'is_public': True,
    }
    response = requests.post(f'{url}channels/create/v2', json = data_obj_1)
    assert response.json() == {'channel_id': 0}

    # Create a channel using user_2
    data_obj_2 = {
    'token': user_2['token'],
    'name': 'vampire', 
    'is_public': True,
    }
    response = requests.post(f'{url}channels/create/v2', json = data_obj_2)
    assert response.json() == {'channel_id': 1}

    # Check listall
    result = requests.get(f'{url}channels/listall/v2', {'token':user_1['token']})
    assert result.json() == {
        'channels': [
            {'channel_id': 0, 'name': 'FlandreScarlet'},
            {'channel_id': 1, 'name': 'vampire'},
        ]
    }
    
    # Check list channels of user 1
    result = requests.get(f'{url}channels/list/v2', {'token':user_1['token']})
    assert result.json() == {'channels': [{'channel_id': 0, 'name': 'FlandreScarlet'}]}

    # Check list channels of user 2
    result = requests.get(f'{url}channels/list/v2', {'token':user_2['token']})
    assert result.json() == {'channels': [{'channel_id': 1, 'name': 'vampire'}]}
