import re
from src.data_store import data_store
from src.notifications import create_noti
from src.error import InputError
from src.other import get_channel_info, get_dm_info, get_message_info, get_user_info, update_storage


store = data_store.get()

# If the @handle_str cannot find valid user, DO NOT raise error. treat as normal string
def get_uid_by_handle(user_handle):

    for user in store['users']:
        if user['user_handle'] == user_handle:
                return user['id']
    return None


def check_tagging(u_id, c_dm_id, is_DM):
    if not is_DM:
        channel = get_channel_info(c_dm_id)
        if u_id in channel['member']:
            return True, channel['name']
    else:
        dm = get_dm_info(c_dm_id)
        if u_id in dm['member']:
            return True, dm['name']
    return False,''


def message_tagging(uid_who_tag, m_str, c_dm_id, is_DM):
    
    # re check string has format @user_handle ends with non-alphanumeric character or end of message
    # use set() to remove possible dulipcate user_handle
    handle_set = re.findall(r'@[a-zA-Z0-9]*', m_str)
    if handle_set:
        handle_set = set([x[1:] for x in handle_set])
    else:
        return
    do_tagging = False
    name = ''
    for handle in handle_set:
        u_id = get_uid_by_handle(handle)
        if u_id is not None:
            do_tagging, name= check_tagging(u_id, c_dm_id, is_DM)
            if do_tagging:
                user_handle = get_user_info(uid_who_tag)['user_handle']
                if not is_DM:
                    create_noti(u_id, 1, user_handle, name, c_id = c_dm_id, noti_message = m_str[0:20])
                else:
                    create_noti(u_id, 1, user_handle, name, dm_id = c_dm_id, noti_message = m_str[0:20])
    return


def have_access_to_message(u_id, message):
    if message['is_DM']:
        dm = get_dm_info(message['dm_id'])
        if u_id in dm['member']:
            return True
        raise InputError(description = 'message belongs to DM that user did not join')
    channel = get_channel_info(message['c_id'])
    if u_id in channel['member']:
        return True
    raise InputError(description = 'message belongs to channel that user did not join')


def react_user_check(u_id, message, react_id):
    valid_react = [1]
    if react_id not in valid_react:
        raise InputError(description = 'Invalid react id')
    have_access_to_message(u_id, message)
 

def react_send_noti(auth_u_id, message):
    auth_user = get_user_info(auth_u_id)
    if message['is_DM']:
        dm = get_dm_info(message['dm_id'])
        if message['creator'] in dm['member']:
            create_noti(message['creator'], 2, auth_user['user_handle'], dm['name'], dm_id = message['dm_id'])
        return
    channel = get_channel_info(message['c_id'])
    if message['creator'] in channel['member']:
        create_noti(message['creator'], 2, auth_user['user_handle'], channel['name'], c_id = message['c_id'])
    return


def already_reacted_check(message, u_id):
    for react in message['reacts']:
        if u_id in react['u_ids']:
                raise InputError(description = 'Message already contains react from user')


def message_react(u_id, m_id, react_id):
    
    message = get_message_info(m_id)
    react_user_check(u_id, message, react_id)
    
    have_reacted = 0
    if message['reacts']:
        already_reacted_check(message, u_id)
        for react in message['reacts']:
            if react['react_id'] == react_id:
                react['u_ids'].append(u_id)
                have_reacted = 1
                break
    # This influence the coverage. Since we SHOULD support different react ids, while assignment specs
    # only mentioned 1 as valid react id
    elif not have_reacted:
        message['reacts'].append(
            {
                'react_id': react_id,
                'u_ids': [u_id],
            }
        )
    react_send_noti(u_id, message)
    update_storage(store)
    return {}


def message_unreact(u_id, m_id, react_id):

    message = get_message_info(m_id)
    react_user_check(u_id, message, react_id)
    have_same_react = 0
    if not message['reacts']:
        raise InputError(description = 'Message does not have reacts')
    for react in message['reacts']:
        if react['react_id'] == react_id:
            have_same_react = 1
            if u_id not in react['u_ids']:
                raise InputError(description = 'User doesn\'t react to message with provided react ID')
            react['u_ids'].remove(u_id)
            break
    # This influence the coverage. Since we SHOULD support different react ids, while assignment specs
    # only mentioned 1 as valid react id
    if not have_same_react:
        raise InputError(description = 'Message does not contain any react with provided react ID')
    return {}