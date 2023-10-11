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

# Invalid email address. still return 200 status due to security concern
def test_invalid_pw_reset_request(user_1):
    resp = requests.post(f"{url}auth/passwordreset/request/v1",json = {'email': 'xxx@gmail.com'})
    assert resp.status_code == 200
    # User 1's pw should not get reset
    resp = requests.post(f"{url}auth/login/v2", json = {'email': "email0@gmail.com", "password": "password0"})
    assert resp.status_code == 200


# Valid pw reset request. user should get logout and couldn't login in
def test_valid_pw_reset_request(user_1):
    resp = requests.post(f"{url}auth/passwordreset/request/v1",json = {'email': 'email0@gmail.com'})
    assert resp.status_code == 200
    # user 1 try to logout and failed
    resp = requests.post(f'{url}auth/logout/v1', json = {'token': user_1['token']})
    assert resp.status_code == 403
    # user 1 try to login without set new pw should fail
    resp = requests.post(f"{url}auth/login/v2", json = {'email': "email0@gmail.com", "password": "password0"})
    assert resp.status_code == 400


def test_invalid_pw_reset(user_1):
    requests.post(f"{url}auth/passwordreset/request/v1",json = {'email': 'email0@gmail.com'})
    resp = requests.post(f"{url}auth/passwordreset/reset/v1",json = {
        'reset_code': 'AD8A7S8H22',
        'new_password': 'yspxcm103jda',
    })
    assert resp.status_code == 400
    