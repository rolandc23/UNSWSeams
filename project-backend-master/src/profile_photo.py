from urllib.error import URLError
import requests, os, pathlib, imgspy
from PIL import Image
from src.config import url
from src.other import get_user_info, update_storage
from src.data_store import data_store
from src.error import InputError

store = data_store.get()

def image_check(url, x_s, y_s, x_e, y_e):
    try:
        im_info = imgspy.info(url)
    except URLError as e:
        raise InputError(description= 'Fetch image from img_url failed') from e
    if im_info['type'] != 'jpg':
        raise InputError(description= 'image uploaded is not a JPG')
    if x_s < 0 or y_s < 0 or x_e <= x_s or y_e <= y_s:
            raise InputError(description= 'Invalid coordinate for image crop')
    if any(x > im_info['width'] for x in (x_s,x_e)) or any(y > im_info['height'] for y in (y_s, y_e)):
            raise InputError(description= 'Invalid coordinate for image crop')



def process_image(url, u_id, x_s, y_s, x_e, y_e):

    r = requests.get(url, stream= True)
    curr_path = os.getcwd() + '/userImage'
    pathlib.Path(curr_path).mkdir(parents= False, exist_ok= True)
    filename = f'{curr_path}/{u_id}.jpg'
    # Usage suggested from requests handbook
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(4096):
            f.write(chunk)
    with Image.open(filename) as im:
        im_new = im.crop((x_s, y_s, x_e, y_e))
        im_new.save(filename)


def upload_profile_image(u_id, img_url, x_s, y_s, x_e, y_e):

    user = get_user_info(u_id) 
    image_check(img_url, x_s, y_s, x_e, y_e)
    process_image(img_url, u_id, x_s, y_s, x_e, y_e)
    user['profile_img_url'] = f'{url}profileAvatar?u_id={u_id}'
    update_storage(store)
    return {}