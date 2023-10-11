
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import get_message_info, get_channel_info, get_dm_info, get_user_info, update_storage

store = data_store.get()

def message_pin_v1(u_id, m_id, mode):

    c_dm_obj = None
    msg = get_message_info(m_id)

    if msg['is_DM']:
        c_dm_obj = get_dm_info(msg['dm_id'])
    else:
        c_dm_obj = get_channel_info(msg['c_id'])

    pin_perm_check(u_id, c_dm_obj, msg['is_DM'])
    # mode 1 indicates pin msg. mode 0 unpin it
    if mode:
        if msg['is_pinned']:
            raise InputError(description = 'This message is pinned already ')
        msg['is_pinned'] = True
    else:
        if not msg['is_pinned']:
            raise InputError(description = 'This message is not pinned yet')
        msg['is_pinned'] = False
    update_storage(store)
    return {}


def pin_perm_check(u_id, c_dm_obj, is_dm):
    
    if u_id not in c_dm_obj['member']:
        raise InputError(description = 'Message is not in any channel/DM you have joined')
    else:
        if is_dm:
            if u_id != c_dm_obj['owner']:
                raise AccessError(description = 'You do not have owner permissions within this DM')
        else:
            user = get_user_info(u_id)
            if u_id not in c_dm_obj['owner'] and user['perm_id'] != 1:
                raise AccessError(description = 'You do not have owner permissions within this Channel')


