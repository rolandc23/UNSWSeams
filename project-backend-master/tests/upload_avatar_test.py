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


def test_invalid_coord(user_1):
    parameter = {
        'token': user_1['token'],
        'img_url': 'https://c-ssl.duitang.com/uploads/item/201811/17/20181117075007_edcto.jpg',
        'x_start':0,
        'y_start':-1,
        'x_end':50,
        'y_end':50,
    }
    rep = requests.post(f'{url}user/profile/uploadphoto/v1', json=parameter)
    assert rep.status_code == 400
    parameter = {
        'token': user_1['token'],
        'img_url': 'https://c-ssl.duitang.com/uploads/item/201811/17/20181117075007_edcto.jpg',
        'x_start':-1,
        'y_start':0,
        'x_end':50,
        'y_end':50,
    }
    rep = requests.post(f'{url}user/profile/uploadphoto/v1', json=parameter)
    assert rep.status_code == 400
    parameter = {
        'token': user_1['token'],
        'img_url': 'https://c-ssl.duitang.com/uploads/item/201811/17/20181117075007_edcto.jpg',
        'x_start':100,
        'y_start':0,
        'x_end':50,
        'y_end':50,
    }
    rep = requests.post(f'{url}user/profile/uploadphoto/v1', json=parameter)
    assert rep.status_code == 400
    parameter = {
        'token': user_1['token'],
        'img_url': 'https://c-ssl.duitang.com/uploads/item/201811/17/20181117075007_edcto.jpg',
        'x_start':0,
        'y_start':100,
        'x_end':50,
        'y_end':50,
    }
    rep = requests.post(f'{url}user/profile/uploadphoto/v1', json=parameter)
    assert rep.status_code == 400
    parameter = {
        'token': user_1['token'],
        'img_url': 'https://c-ssl.duitang.com/uploads/item/201811/17/20181117075007_edcto.jpg',
        'x_start':0,
        'y_start':0,
        'x_end':1200,
        'y_end':50,
    }
    rep = requests.post(f'{url}user/profile/uploadphoto/v1', json=parameter)
    assert rep.status_code == 400
    parameter = {
        'token': user_1['token'],
        'img_url': 'https://c-ssl.duitang.com/uploads/item/201811/17/20181117075007_edcto.jpg',
        'x_start':0,
        'y_start':0,
        'x_end':60,
        'y_end':2000,
    }
    rep = requests.post(f'{url}user/profile/uploadphoto/v1', json=parameter)
    assert rep.status_code == 400
    parameter = {
        'token': user_1['token'],
        'img_url': 'https://c-ssl.duitang.com/uploads/item/201804/21/20180421175534_yzfFm.png',
        'x_start':0,
        'y_start':0,
        'x_end':200,
        'y_end':200,
    }
    rep = requests.post(f'{url}user/profile/uploadphoto/v1', json=parameter)
    assert rep.status_code == 400
    parameter = {
        'token': user_1['token'],
        'img_url': 'https://xzc22.com.4_p0.jpg',
        'x_start':0,
        'y_start':0,
        'x_end':200,
        'y_end':200,
    }
    rep = requests.post(f'{url}user/profile/uploadphoto/v1', json=parameter)
    assert rep.status_code == 400

def test_valid_upload(user_1):
    # test default profile
    resp = requests.get(f'{url}user/profile/v1', {'token': user_1['token'], 'u_id': user_1['auth_user_id']}).json()
    u_image_url = resp['user']['profile_img_url']
    resp = requests.get(u_image_url)
    assert resp.status_code == 200
    # Upload new avatar
    parameter = {
        'token': user_1['token'],
        'img_url': 'https://c-ssl.duitang.com/uploads/item/201811/17/20181117075007_edcto.jpg',
        'x_start':172,
        'y_start':26,
        'x_end':551,
        'y_end':260,
    }
    rep = requests.post(f'{url}user/profile/uploadphoto/v1', json=parameter)
    assert rep.status_code == 200
