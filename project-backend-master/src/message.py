import threading
from datetime import datetime
from src.data_store import data_store
from src.channel import channel_user_check
from src.messageReactTagging import message_tagging
from src.other import (get_channel_info, update_storage, 
    get_message_info, get_dm_info, get_user_info, get_dm_info, create_m_id, store_message)
from src.error import InputError, AccessError
from src.user_stats import user_stat_update
from src.seam_stats import sys_stat_update

store = data_store.get()

def delay_store_message(message, tagging_option):
    
    store_message(message)

    if tagging_option:
        if message['is_DM']:
            message_tagging(message['creator'], message['message'], message['dm_id'], True)
        else:
            message_tagging(message['creator'], message['message'], message['c_id'], False)
    user_stat_update(message['creator'], 3, 1)
    sys_stat_update(3, 1)
    update_storage(store)
    return


def send_message_core(u_id, c_dm_id, message_str, mode, is_delay, timestamp, enable_tagging):
    if len(message_str) < 1 or len(message_str) > 1000:
        raise InputError(description = 'message string not valid')
    # Mode 1 for channel. Mode 2 for DM
    now = int(datetime.now().timestamp())
    id = create_m_id()
    new_message = {
        'm_id': id,
        'creator': u_id,
        'message': message_str,
        'time_sent': now,
        'reacts': [],
        'is_pinned': False,
    }
    if mode == 1:
        new_message['c_id'] = c_dm_id
        new_message['is_DM'] = False
    else:
        new_message['dm_id'] = c_dm_id
        new_message['is_DM'] = True
    if is_delay:
        if now > timestamp:
            raise InputError(description = 'Time_sent is a time in the past')
        new_message['time_sent'] = timestamp
        sec = timestamp - now
        t = threading.Timer(sec,delay_store_message, [new_message, enable_tagging])
        t.start()
    else:
        delay_store_message(new_message, enable_tagging)
    return id

def send_messages_mix(u_id, c_dm_id, message_str, mode, is_delay= False, timestamp= None, enable_tagging= True):
    '''
    This function creates messages and returns the time they were sent

    Arguments: 
        token - token of authorised user 
        c_dm_id (string) - ID of valid channel/dm
        message_str (string) - String of message sent
        mode (1 or 2) - 1 for channel. 2 for dm
        is_delay - Delayed for storing this message
        timestamp - How long the delayed should be


    Exceptions:
        InputError - Occurs when the channel does not exist
        AccessError - Occurs when the user does not exist in the list
        AccessError - Occurs when the user is not in the channel

    Return Value: 
        Returns message id
    '''
    if mode == 1:
        # Checks error cases of channel_details
        channel_user_check(u_id, c_dm_id)
        new_m_id = send_message_core(u_id, c_dm_id, message_str, mode, is_delay, timestamp, enable_tagging)
    else:
        # Raises input error if DM does not exist
        dm_info = get_dm_info(c_dm_id)
        if u_id not in dm_info['member']:
            raise AccessError(description = "Authorised user is not participant of DM")
        new_m_id = send_message_core(u_id, c_dm_id, message_str, mode, is_delay, timestamp, enable_tagging)
    # Return { message_id }
    return {'message_id': new_m_id}


# Helper function to check if user is able to edit DM
def check_edit_DM(message, u_id):
    dm =  get_dm_info(message['dm_id']) # Searches dm list with m_id, returns dm if exists
    if u_id != message['creator'] and u_id != dm['owner']: # if the given u_id is not creator, raise AccessError
        raise AccessError(description = 'user has no permission to edit')


# Helper function to check if user is able to edit channel
def check_edit_CH(message, u_id):
    channel = get_channel_info(message['c_id']) # Searches channel list with c_id, returns channel if exists
    user = get_user_info(u_id) 
    if u_id != message['creator']: # if user is not creator
        if u_id in channel['member']: # if user is a member of channel
            if u_id not in channel['owner'] and user['perm_id'] != 1:
                raise AccessError(description = 'user has no permission to edit')
        else:
            raise InputError(description = 'm_id does not refer to a valid message for channels auth user joined')


# Function to check edit permissions of user given their token, and message wish to edit
def check_edit_perms(message, u_id):
    
    if message['is_DM']:
        check_edit_DM(message, u_id)
    
    else:
        check_edit_CH(message, u_id)
    

# Given the message string and ID, edits it
def edit_message(m_str, m_id, u_id):
    
    message = get_message_info(m_id)
    check_edit_perms(message, u_id)
    
    # error checking for string length
    if len(m_str) > 1000:
        raise InputError(description = 'message string not valid')

    # if given m_string is empty, remove it from data store. Essentially is deleting message
    if m_str == '':
        store['messages'].remove(message)
        sys_stat_update(3, (-1))

    # updating message list
    message['message'] = m_str

    if message['is_DM']:
        message_tagging(u_id, m_str, message['dm_id'], True)
    else:
        message_tagging(u_id, m_str, message['c_id'], False)
    update_storage(store)
        
    return {}


# Given message id, removes message
def remove_message(mess_id, u_id):
    
    '''
    Given a message_id for a message, this message is removed from the channel/DM
    
    Arguments:
        mess_id (int) - id of target message
        token (str) - JWT containing { u_id, session_id }

    Return Value:
        {}
    
    '''

    message = get_message_info(mess_id)

    check_edit_perms(message, u_id)

    # Delete from store
    store['messages'].remove(message)
    
    sys_stat_update(3, (-1))
    update_storage(store)
        
    return {}

