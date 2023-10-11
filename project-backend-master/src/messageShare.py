from src.error import AccessError, InputError
from src.other import (get_message_info, get_dm_info, get_channel_info, 
                    get_user_info, create_m_id,
                    update_storage, store_message)
from src.messageReactTagging import message_tagging, have_access_to_message
from src.data_store import data_store
from datetime import datetime
from src.user_stats import user_stat_update
from src.seam_stats import sys_stat_update

store = data_store.get()

def message_share_check(u_id, m_id, m_str, c_id, dm_id):
    send_mode = -1
    c_dm = 0

    if c_id == -1 and dm_id == -1:
        raise InputError(description = 'Neither channel_id nor dm_id are valid')
    elif c_id != -1 and dm_id == -1:
        c_dm = get_channel_info(c_id)
        send_mode = 1
    elif dm_id != -1 and c_id == -1:
        c_dm = get_dm_info(dm_id)
        send_mode = 2
    else:
        raise InputError(description = 'Invalid parameters format of channel_id and dm_id')
    
    # Test if message id is valid, but cannot accessed by user
    m_object = get_message_info(m_id)
    have_access_to_message(u_id, m_object)
    
    if len(m_str) > 1000:
        raise InputError(description = 'Length of message more than 1000 characters')

    user = get_user_info(u_id)

    if user['id'] not in c_dm['member']:
        raise AccessError(description = 'User not in the channel/dm that tries to share message')

    return m_object['message'], send_mode, c_dm


def message_share_send(u_id, old_str, m_str, c_dm_id, mode):

    now = int(datetime.now().timestamp())
    m_id = create_m_id()
    new_message = {
        'm_id': m_id,
        'creator': u_id,
        'message': old_str + '.' + m_str,
        'time_sent': now,
        # Message is not deleted by default
        'reacts': [],
        'is_pinned': False,
    }
    # Mode 1 means sharing to channel
    # Mode 2 means sharing to dm
    if mode == 1:
        new_message['c_id'] = c_dm_id
        new_message['is_DM'] = False
    else:
        new_message['dm_id'] = c_dm_id
        new_message['is_DM'] = True
    store_message(new_message)
    message_tagging(u_id, new_message['message'], c_dm_id, new_message['is_DM'])
    
    user_stat_update(u_id, 3, 1)
    sys_stat_update(3, 1)
    update_storage(store)
    return {'shared_message_id': m_id}

def message_share(u_id, m_id, c_id, dm_id, m_str =''):
    old_str, mode, c_dm = message_share_check(u_id, m_id, m_str, c_id, dm_id)
    return message_share_send(u_id, old_str, m_str, c_dm['id'], mode)
