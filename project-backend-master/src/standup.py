from src.error import AccessError, InputError
from src.other import get_channel_info, update_storage, get_user_info
from src.message import send_messages_mix
from datetime import datetime
from src.data_store import data_store
import threading

global store
store = data_store.get()

def standup_start_v1(u_id, c_id, length):

    # Check if user is in channel, also raises InputError if c_id is invalid
    if u_id not in get_channel_info(c_id)['member']:
        raise AccessError(description= 'User is not in channel')

    # Check if standup is already active
    elif standup_active_v1(u_id, c_id)['is_active']:
        raise InputError(description= 'Channel already has an active standup')
    
    # Check if length is not negative
    elif length <= 0:
        raise InputError(description= 'Length of standup cannot be negative or 0')

    # Establish start and finish times of standup
    now = int(datetime.now().timestamp())
    finish = now + length

    # Initialise and define new standup and append to data store
    standup = {
        'u_id': u_id,
        'c_id': c_id,
        'time_finish': finish,
        'message_list': []
    }
    store['standups'].append(standup)
    update_storage(store)

    # Start timer
    threading.Timer(length, standup_complete_v1, [u_id, c_id]).start()
    
    return {'time_finish': finish}


def get_standup_info(c_id):
    for standup in store['standups']:
        if c_id == standup['c_id']:
            return [True, standup['time_finish']]
    return [False, None]


def standup_active_v1(u_id, c_id):

    # Check if user is in channel, also raises InputError if c_id is invalid
    if u_id not in get_channel_info(c_id)['member']:
        raise AccessError(description= 'User is not in channel')

    status, finish = get_standup_info(c_id)
    return {
        'is_active': status,
        'time_finish': finish
    }


def standup_send_v1(u_id, c_id, message_str):
    
    str_len = len(message_str)
    # Check if user is in channel, also catches InputError if c_id is invalid
    if u_id not in get_channel_info(c_id)['member']:
        raise AccessError(description = 'User is not in channel')

    # Check if message string is valid
    elif str_len > 1000 or str_len < 1:
        raise InputError(description = 'message string not valid')

    # Check if standup is not active
    elif not standup_active_v1(u_id, c_id)['is_active']:
        raise InputError(description = 'Standup is not active in channel')
    
    for standup in store['standups']:
        if c_id == standup['c_id']:
            standup['message_list'].append(f"{get_user_info(u_id)['user_handle']}: {message_str}")
    
    update_storage(store)

    return {}


def standup_complete_v1(u_id, c_id):

    message = ''
    for standup in store['standups']: # pragma: no branch
        if standup['c_id'] == c_id:
            message = "\n".join(standup['message_list'])
            store['standups'].remove(standup)
            break

    if message != '':
        send_messages_mix(u_id, c_id, message, 1, enable_tagging=False)

    update_storage(store)