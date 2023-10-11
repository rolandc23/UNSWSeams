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
def user_3():
    data_obj = {
        'email': 'email2@gmail.com', 
        'password': 'password2',
        'name_first': 'User', 
        'name_last': 'Thired'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    return response.json()

############################ TEST REGISTER-LOGIN ############################

# Simple registration test
def test_register(user_1, user_2):
    id_0 = user_1['auth_user_id']
    id_1 = user_2['auth_user_id']
    assert id_0 != id_1


# Test instance of multiple tokens
def test_multi_login_session(user_1):
    # Register
    token_1 = user_1['token']
    data_obj = {
        'email': 'email0@gmail.com', 
        'password': 'password0',
    }

    # First login
    response = requests.post(f'{url}auth/login/v2',json = data_obj)
    token_2 = response.json()['token']

    # Check different token
    assert token_1 != token_2

    # Check logout after logged out already
    requests.post(f'{url}auth/logout/v1', json = {'token': user_1['token']})
    response = requests.post(f'{url}auth/logout/v1', json = {'token': user_1['token']})
    assert response.status_code == 403


# Test invalid login input
def test_login_invalid(user_1):
    # Log out
    requests.post(f'{url}auth/logout/v1', json = {'token': user_1['token']})

    # InputError: Invalid email
    data_obj = {
        'email': 'email0@gg.com', 
        'password': 'password0',
    }
    response = requests.post(f'{url}auth/login/v2',json = data_obj)
    assert response.status_code == 400

    # InputError: Invalid password
    data_obj = {
        'email': 'email0@gmail.com',
        'password': 'password',
    }
    response = requests.post(f'{url}auth/login/v2',json = data_obj)
    assert response.status_code == 400

    
# InputError: Invalid name cases
def test_invalid_name():
    # Invalid first name
    data_obj = {
        'email': 'e@gmail.com', 
        'password': 'passczklm',
        'name_first': '@!*&', 
        'name_last': 'Second'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    assert response.status_code == 400

    # Invalid last name
    data_obj = {
        'email': 'e@gmail.com', 
        'password': 'passczklm',
        'name_first': 'PPPPP', 
        'name_last': '-=$$'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    assert response.status_code == 400  

    # Last name too long
    data_obj = {
        'email': 'e@gmail.com', 
        'password': 'passczklm',
        'name_first': 'PPPPP', 
        'name_last': 'x'*51,
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    assert response.status_code == 400

    # Empty first name
    data_obj = {
        'email': 'e@gmail.com', 
        'password': 'passczklm',
        'name_first': '', 
        'name_last': 'zzzz'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    assert response.status_code == 400


# InputError: Test invalid email entries
def test_register_invalid_email():
    # Invalid .com
    data_obj = {
        'email': 'abc123@gmail.c', 
        'password': 'password0',
        'name_first': 'User', 
        'name_last': 'First'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    assert response.status_code == 400

    # No @email
    data_obj = {
        'email': 'abc123.com', 
        'password': 'password0',
        'name_first': 'User', 
        'name_last': 'First'
    }    
    
    # No email name
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    assert response.status_code == 400
    data_obj = {
        'email': '@.com', 
        'password': 'password0',
        'name_first': 'User', 
        'name_last': 'First'
    }   

    # No '.'
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    assert response.status_code == 400
    data_obj = {
        'email': 'abc123@gmailcom', 
        'password': 'password0',
        'name_first': 'User', 
        'name_last': 'First'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    assert response.status_code == 400


# InputError: Test duplicate email
def test_register_existing_email(user_1):
    # User 1 is already registered with same details
    data_obj = {
        'email': 'email0@gmail.com', 
        'password': 'hunkybunky',
        'name_first': 'User', 
        'name_last': 'First'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    response.status_code == 400


# InputError: Test bad password
def test_register_invalid_pw():
    # Password too short
    data_obj = {
        'email': 'abc123@gmail.com', 
        'password': 'p00',
        'name_first': 'User', 
        'name_last': 'First'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    assert response.status_code == 400

# Test login with unregistered email
def test_email_unregistered():
    requests.delete(f'{url}clear/v1')
    data_obj = {
        'email': 'email2@gmail.com', 
        'password': 'password2',
    }
    fail_1 = requests.post(f'{url}auth/login/v2',json = data_obj)
    assert fail_1.status_code == 400


# Test logout/login functionality
def test_logout_login(user_1):
    token = user_1['token']
    u_id = user_1['auth_user_id']
    
    requests.post(f'{url}auth/logout/v1', json = {'token': token})
    # AccessError: User logout. token invalid so raise 403 error
    response = requests.get(f'{url}user/profile/v1', {'token': token, 'u_id': u_id})
    assert response.status_code == 403

    # InputError: Invalid user email
    data_obj = {
        'email': 'emai@lm', 
        'password': 'password0',
    }
    response = requests.post(f'{url}auth/login/v2',json = data_obj)
    assert response.status_code == 400

    # User success login
    data_obj = {
        'email': 'email0@gmail.com', 
        'password': 'password0',
    }
    response = requests.post(f'{url}auth/login/v2',json = data_obj)
    token = response.json()['token']
    response = requests.get(f'{url}user/profile/v1', {'token': token, 'u_id': u_id})
    assert response.json()['user'] == {
        'u_id': u_id,
        'email': 'email0@gmail.com', 
        'name_first': 'User', 
        'name_last': 'First',
        'handle_str': 'userfirst',
        'profile_img_url': f'{url}profileAvatar/default'
    }

# Tests handles of same names
def test_same_handle_profile():
    requests.delete(f'{url}clear/v1')
    # All users with same handle
    data_obj = {
        'email': 'abc1230@gmail.com', 
        'password': 'EldenRing0',
        'name_first': 'Thisnameis', 
        'name_last': '20letterss232'
    }
    data_obj_1 = {
        'email': 'abc1231@gmail.com', 
        'password': 'EldenRing1',
        'name_first': 'Thisnameis', 
        'name_last': '20letterss11'
    }
    data_obj_2 = {
        'email': 'abc1232@gmail.com', 
        'password': 'EldenRing2',
        'name_first': 'Thisnameis', 
        'name_last': '20letterss000'
    }

    # Check handle creation behaviour is correct
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    requests.post(f'{url}auth/register/v2', json = data_obj_1)
    requests.post(f'{url}auth/register/v2', json = data_obj_2)

    user_profile = requests.get(f'{url}users/all/v1', {'token': response.json()['token']})
    user_profile = user_profile.json()['users']

    assert user_profile[0]['handle_str'] == 'thisnameis20letterss'
    assert user_profile[1]['handle_str'] == 'thisnameis20letterss0'
    assert user_profile[2]['handle_str'] == 'thisnameis20letterss1'

############################ TEST USER-CALLED FUNCTIONS ############################

# AccessError: Test calling user/all function with invalid token
def test_userall_invalid_token():
    response = requests.get(f'{url}users/all/v1', {
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjAsIlNlc3Npb25faWQiOjExfQ.DhmZZZZZxhZA20vGy5h04kR6BAdAyMcrjrPUcWv3CuI'})
    assert response.status_code == 403


# Test calling single profile
def test_profile_single(user_1):
    user_profile = requests.get(f'{url}user/profile/v1', {'token': user_1['token'], 'u_id': 0})
    assert user_profile.json()['user'] == {
        'u_id': user_1['auth_user_id'],
        'email': 'email0@gmail.com', 
        'name_first': 'User', 
        'name_last': 'First',
        'handle_str': 'userfirst',
        'profile_img_url': f'{url}profileAvatar/default'
    }

# InputError: Test invalid u_id for profile
def test_profile_invalid_uid(user_1):
    response = requests.get(f'{url}user/profile/v1', {'token': user_1['token'], 'u_id': 666})
    assert response.status_code == 400


# AccessError: Test invalid token for calling profile
def test_profile_invalid_token():
    response = requests.get(f'{url}user/profile/v1', {
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjAsIlNlc3Npb25faWQiOjExfQ.DhmZZZZZxhZA20vGy5h04kR6BAdAyMcrjrPUcWv3CuI', 'u_id': 0})
    assert response.status_code == 403


# Check set email valid
def test_set_email(user_1,user_2):
    requests.put(f'{url}user/profile/setemail/v1', json = {
        'token': user_2['token'],
        'email': 'zmmmm@student.unsw.edu.au'
    })
    user_profile = requests.get(f'{url}user/profile/v1', {'token': user_2['token'], 'u_id': 1})
    assert user_profile.json()['user']['email'] == 'zmmmm@student.unsw.edu.au'


# Check set name valid
def test_set_name(user_1, user_2, user_3):
    requests.put(f'{url}user/profile/setname/v1', json = {
        'token': user_2['token'],
        'name_first': 'Hidetaka',
        'name_last': 'Miyazaki'
    })
    user_profile = requests.get(f'{url}user/profile/v1', {'token': user_2['token'], 'u_id': 1})
    assert user_profile.json()['user']['name_first'] == 'Hidetaka'
    assert user_profile.json()['user']['name_last'] == 'Miyazaki'


# Check set handle valid
def test_set_handle(user_1, user_2, user_3):
    requests.put(f'{url}user/profile/sethandle/v1', json = {
        'token': user_3['token'],
        'handle_str': 'pdnasndc'
    })
    user_profile = requests.get(f'{url}user/profile/v1', {'token': user_3['token'], 'u_id': 2})
    assert user_profile.json()['user']['handle_str'] == 'pdnasndc'

# Test handle already used
def test_set_handle_duplicate(user_1, user_2, user_3):
    response = requests.put(f'{url}user/profile/sethandle/v1', json = {
        'token': user_1['token'],
        'handle_str': 'usersecond',
    })
    assert response.status_code == 400


# InputError: Test handle too long
def test_set_long_handle(user_1):
    response = requests.put(f'{url}user/profile/sethandle/v1', json = {
    'token': user_1['token'],
    'handle_str': 'q'*21,
    })
    assert response.status_code == 400


# InputError: Test handle too short
def test_set_short_handle(user_1):
    response = requests.put(f'{url}user/profile/sethandle/v1', json = {
    'token': user_1['token'],
    'handle_str': 'q'*2,
    })
    assert response.status_code == 400


# InputError: Test invalid keys for handle
def test_invalid_key(user_1):
    response = requests.put(f'{url}user/profile/sethandle/v1', json = {
    'token': user_1['token'],
    'handle_str': '#**()*()!!',
    })
    assert response.status_code == 400

def test_user_name_has_number():
    requests.delete(f'{url}clear/v1')
    data_obj = {
        'email': 'xxxx@gmail.com', 
        'password': 'password0',
        'name_first': 'abc', 
        'name_last': 'def0'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)

    
    data_obj = {
        'email': 'xxxx23@gmail.com', 
        'password': 'password0',
        'name_first': 'abc', 
        'name_last': 'def'
    }
    requests.post(f'{url}auth/register/v2',json = data_obj)
    

    data_obj = {
        'email': 'xxxx77@gmail.com', 
        'password': 'password0',
        'name_first': 'abc', 
        'name_last': 'def'
    }
    response = requests.post(f'{url}auth/register/v2',json = data_obj)
    u_2 = response.json()
    user_profile = requests.get(f'{url}user/profile/v1', {'token': u_2['token'], 'u_id': 2})
    assert user_profile.json()['user']['handle_str'] == 'abcdef1'
