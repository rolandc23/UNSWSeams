from src.data_store import data_store
from src.error import AccessError, InputError
from src.notifications import create_noti
from src.other import (get_user_info,
                       get_lists_user_info,
                       update_storage, set_is_user_reacted,
                       get_dm_info)
from src.user_stats import user_stat_update
from src.seam_stats import sys_stat_update

global store
store = data_store.get()


def dm_create(user_list, owner_id):
    '''
    u_ids contains the user(s) that this DM is directed to, and will not include the creator. 
    The creator is the owner of the DM. name should be automatically generated based on the users 
    that are in this DM. The name should be an alphabetically-sorted, comma-and-space-separated list 
    of user handles, e.g. 'ahandle1, bhandle2, chandle3'.

     Arguments:
        user_list (list) - List of u_ids that the authoerised user is directing the DM to
        token (str) - JWT containing { u_id, session_id }

    Exceptions:
        InputError -  u_id in u_ids does not refer to a valid user
        InputError -  there are duplicate 'u_id's in u_ids

    Return Value:
        Returns a dictionary containing list of dm
    
    '''

    # getting the creator's info from token
    owner_info = get_user_info(owner_id)

    dm_id = 0
    handle_list = [owner_info['user_handle']]

    # Basic error checking
    if len(user_list) != len(set(user_list)):
        raise InputError(description = 'Duplicate of user IDs are in list')

    if owner_id in user_list:
        raise InputError(description = 'Duplicate of user IDs are in list')

    for user_id in user_list:
        user_info = get_user_info(user_id)
        handle_list.append(user_info['user_handle'])


    handle_list.sort()
    dm_name = ', '.join(handle_list)
    final_list =  [owner_id] + user_list

    dm = {
        'id': dm_id,
        'name': dm_name,
        'owner': owner_id,
        'member': final_list,
        'message': [],
    }

    if store['dms']:
        dm_id = max(dm['id'] for dm in store['dms']) + 1

    dm['id'] = dm_id
    store['dms'].append(dm)

    # have to repeat a loop since we need the dm_name
    for u_id in user_list:
        create_noti(u_id, 3, owner_info['user_handle'], dm['name'], dm_id = dm['id'] )
    for dm_member in final_list:
        user_stat_update(dm_member, 2, 1)
    sys_stat_update(2, 1)
    update_storage(store)
    return {'dm_id': dm['id']}


# Returns list of DMs that a user is part of
def dm_list_v1(u_id):

    '''
    Returns list of DMs that a user is part of

    Arguments:
        token (str) -  JWT containing { u_id, session_id }

    Return Value:
        Returns dictionary. Key is 'dms' with values mapping a list of 
        dms which the user is a part of

    '''

    list_of_dms = []
    for dm in store['dms']:
        if u_id in dm['member']:
            list_of_dms.append(
                {
                    'dm_id': dm['id'],
                    'name': dm['name']
                }
            )
    return {'dms': list_of_dms}


# Remove an existing DM, so all members are no longer in the DM. Only done by original creater of DM
def dm_remove_v1(dm_id, u_id):

    '''
    Remove an existing DM, so all members are no longer in the DM.
    This can only be done by the original creator of the DM

    Arguments:
        token (str) - JWT containing { u_id, session_id }
        dm_id (int) - the DM which user is trying to access (its id)
        
    Exceptions:
        AccessError - dm_id is valid and the authorised user is no longer in the DM
        AccessError - dm_id is valid and the authorised user is not the original DM creator
         
    Return Value:
        {}

    '''
    # Raises input error if DM does not exist
    dm_info = get_dm_info(dm_id)

    # dm_id is valid and the authorised user is no longer in the DM 
    if u_id not in dm_info['member']:
        raise AccessError(description = "Authorised user is no longer in DM")
    # dm_id is valid and the authorised user is not the original DM creator
    if dm_info['owner'] != u_id:
        raise AccessError(description = "Authorised user is not original creator of DM")
    
    dm_mid_list = []
    for msg in store['messages']:
        if msg['is_DM'] and msg['dm_id'] == dm_id:
            dm_mid_list.append(msg['m_id'])
    msg_amount = len(dm_mid_list)
    
    # Remove all dm messages belongs to it
    new_msg_list = []
    for msg in store['messages']:
        if msg['m_id'] not in dm_mid_list:
            new_msg_list.append(msg)
    store['messages'] = new_msg_list
    sys_stat_update(3, -(msg_amount))

    for member in dm_info['member']:
        user_stat_update(member, 2, (-1))
    store['dms'].remove(dm_info)
    sys_stat_update(2, (-1))
    update_storage(store)
    return {}


# Given a DM with ID dm_id that the authorised user is a member of, provide basic details about the DM.
def dm_details_v1(dm_id, u_id):

    '''
    Given a DM with ID dm_id that the authorised user is a member of, provide basic details about the DM.

    Arguments:
        token (str) - JWT containing { u_id, session_id }
        dm_id (int) - ID of the DM which user is trying to access 

    Exceptions:
        AccessError - dm_id is valid and the authorised user is not a member of the DM

    Return Value:
        Returns a dictionary with key 'names' and 'members' - basic details of the DM

    '''
    # Raises input error if DM does not exist
    dm_info = get_dm_info(dm_id)

    if u_id not in dm_info['member']:
        raise AccessError(description = "Authorised user is not participant of DM")
    
    member_list = get_lists_user_info(dm_info['member'])
    
    return {'name': dm_info['name'], 'members': member_list}



# Given a DM ID, the user is removed as a member of this DM. 
def dm_leave_v1(dm_id, u_id):

    '''

    Given a DM ID, the user is removed as a member of this DM. The creator is allowed to leave and the
    DM will still exist if this happens. This does not update the name of the DM.

    Arguments:
        token (str) - JWT containing { u_id, session_id }
        dm_id (int) - ID of the DM which user is trying to access 

    Exceptions:
        AccessError
            - dm_id is valid and the authorised user is not a member of the DM
      
    Return Value:
        {}

    '''
    # Raises input error if DM does not exist
    dm_info = get_dm_info(dm_id)

    # AccessError if dm_id is valid and the authorised user is not a member of the DM
    if u_id not in dm_info['member']:
        raise AccessError(description = "Authorised user is not participant of DM")
    
    dm_info['member'].remove(u_id)
    user_stat_update(u_id, 2, (-1))
    if u_id == dm_info['owner']:
        dm_info['owner'] = ''
    update_storage(store)

    return {}


def dm_messages_check(dm_id, start, auth_u_id):
    dm_messages = search_dm_message(dm_id, auth_u_id)

    if start > len(dm_messages):
        raise InputError(description = 'Start point larger than number of messages')

    return dm_messages


def search_dm_message(dm_id, auth_u_id):
    m_list = []
    for message in store['messages']:
        if message['is_DM']:
            if message['dm_id'] == dm_id:
                tmp_react_list = set_is_user_reacted(message, auth_u_id)
                tmp_dict = {
                    'message_id': message['m_id'],
                    'u_id': message['creator'],
                    'message': message['message'],
                    'time_sent': message['time_sent'],
                    'reacts': tmp_react_list,
                    'is_pinned': message['is_pinned'],
                }
                m_list.append(tmp_dict)
    return m_list


def dm_messages_v1(u_id, dm_id, start):

    '''
    Given a DM with ID dm_id that the authorised user is a member of, return up to 50 messages 
    between index "start" and "start + 50". Message with index 0 is the most recent message in the DM.
    This function returns a new index "end" which is the value of "start + 50", or, if this function has
    returned the least recent messages in the DM, returns -1 in "end" to indicate there are no more
    messages to load after this return.

    Arguments:
        token (str) - JWT with { u_id, session_id }
        dm_id (int) - DM ID which the auth user is trying to access within their DMs
        start (int) - starting index of message

    Exceptions:
        InputError - dm_id does not refer to a valid DM
        InputError - start is greater than the total number of messages in the channel
        AccessError - dm_id is valid and the authorised user is not a member of the DM
      
    Return Value:
        Returns dictionary with key:
            'messages' - list of dictionaries with messages information
            'start' - start which was passed into function
            'end' - int with value 'start + 50'. otherwise returns -1 if no more messages to be loaded

    '''
    dm_info = get_dm_info(dm_id)
    dm_messages = dm_messages_check(dm_id, start, u_id)
    m_list = []

    if u_id not in dm_info['member']:
        raise AccessError(description = "Authorised user is not participant of DM")

    total_num_messages = len(dm_messages)
    end = start + 50

    if end >= total_num_messages:
        end = total_num_messages

    for index in range(start, end):
        m_list.append(dm_messages[index])
    
    # returned the least recent messages in the DM, returns -1 in "end" to indicate there are no more messages 
    # to load after this return.
    if end == total_num_messages:
        end = -1
    
    return {
        'messages': m_list,
        'start': start,
        'end': end,
    }
