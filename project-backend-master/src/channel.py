from src.data_store import data_store
from src.error import AccessError, InputError
from src.notifications import create_noti
from src.other import (get_channel_info, get_user_info,
                       get_lists_user_info, set_is_user_reacted, 
                       update_storage)
from src.user_stats import user_stat_update

global store
store = data_store.get()


# Checks error cases of channel_join
def channel_join_check(auth_u_id, c_id):
    
    # Call helper function to receive information about channel
    channel = get_channel_info(c_id)

    # Call helper function to receive information about user
    user = get_user_info(auth_u_id)

    # If user is already member
    if auth_u_id in channel['member']:
        raise InputError(description = 'Already a member of given Channel')

    # If channel is not set to public and user is not Seams owner
    if not channel['is_public']:
        if user['perm_id'] != 1:
            raise AccessError(description = 'Private channel access deny')

    # Else, return channel information if everything is valid
    return channel


# Checks error cases of channel_details
def channel_user_check(auth_u_id, c_id):
    
    # Grabs information about channel
    channel = get_channel_info(c_id)

    # If user is not member of channel
    if auth_u_id not in channel['member']:
        raise AccessError(description = 'Authorised user not in the channel')

    # Return channel information if everything is valid
    return channel


# Checks error cases of channel_invite
def channel_invite_check(auth_u_id, c_id, u_id):

    # Grab channel information
    channel = get_channel_info(c_id)

    # This actually test if u_id invalid
    get_user_info(u_id)

    # If auth_user is not member of channel
    if auth_u_id not in channel['member']:
        raise AccessError(description = 'auth_user not in the channel')

    # If invited user is already member
    elif u_id in channel['member']:
        raise InputError(description = 'Already a member of given Channel')

    # Return channel information if all is valid
    return channel


def channel_owner_related_check(auth_u_id, u_id, c_id, function_mode):
    
    channel = get_channel_info(c_id)
    auth_user = get_user_info(auth_u_id)

    if auth_u_id not in channel['member']:
        raise AccessError(description = 'auth user does not in the channel')
    elif auth_u_id not in channel['owner'] and (auth_user['perm_id'] != 1):
        raise AccessError(description = 'auth user does not have owner permissions')
    
    user = get_user_info(u_id)

    if user['id'] not in channel['member']:
        raise InputError(description = 'u_id refer to a user who is not a member of channel')
    # function_mode used to swtich function behavior betwwen addowner/removeowner.
    # function_mode = 1 indicates addowner
    if function_mode:
        if user['id'] in channel['owner']:
            raise InputError(description = 'u_id refer to a user who is already an owner of channel')
    else:
        if user['id'] not in channel['owner']:
            raise InputError(description = 'u_id refer to a user who is not an owner of channel')
        elif len(channel['owner']) == 1:
            raise InputError( description = 'Unable to remove the last owner of channel')
    return channel


def search_channel_message(c_id, auth_u_id):
    m_list = []
    for message in store['messages']:
        if not message['is_DM']:
            if message['c_id'] == c_id:
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


def channel_messages_check(auth_u_id, c_id, start):

    # Standard channel-user info check
    channel_user_check(auth_u_id, c_id)
    channel_messages = search_channel_message(c_id, auth_u_id)

    if start > len(channel_messages):
        raise InputError(description = 'Start point larger than number of messages')

    # Else return channel information
    return channel_messages


def channel_details_v1(auth_user_id, channel_id):
    '''
    This function allows an authorised user (who is a member of a valid channel) to check the details of that channel

    Arguments:
        auth_user_id (integer) - The ID of the authorised user
        channel_id (integer) - The ID of a valid channel

    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        AccessError - Occurs when channel_id DOES refer to a valid channel, but the authorised user is not in the channel

    Return Value:
        Returns a dictionary containing channel details - this includes the name of the channel, information about the 
        channel's privacy setting (public or private), a list of owner members and a list of other members
    '''
    # Calls helper function to find information about the channel with input ID
    channel = channel_user_check(auth_user_id, channel_id)

    # Grabs list of owner and members of the channel
    owner_list = get_lists_user_info(channel['owner'])
    member_list = get_lists_user_info(channel['member'])


    # Returning details of the channel
    return {
        'name': channel['name'],
        'is_public': channel['is_public'],
        'owner_members': owner_list,
        'all_members': member_list,
    }


def channel_join_v1(auth_u_id, c_id):
    '''
    This function adds an authorised user to a valid channel with c_id

    Arguments:
        auth_u_id (integer) - The ID of the authorised user
        c_id (integer) - The ID of an existing channel

    Exceptions:
        InputError - Occurs when c_id does not refer to a valid channel
        InputError - Occurs when the authorised user is already a member of the valid channel
        AccessError - Occurs when c_id is a private channel and the authorised user 
        is not a global owner

    Return Value:
        Returns an empty dictionary
    '''
    # Calls helper function to determine whether joining user has permission to join
    channel = channel_join_check(auth_u_id, c_id)

    # If valid, add user to members list of chanel
    channel['member'].append(auth_u_id)

    user_stat_update(auth_u_id, 1, 1)

    update_storage(store)
    return {}


def channel_invite_v1(auth_u_id, c_id, u_id):
    '''
    An authorised user who is a member of a channel invites another user to join the channel

    Arguments:
        auth_u_id (integer) - the ID of the authorised user - the caller 
        c_id (integer) - the ID of an existing channel 
        u_id (integer) - the ID of the user to be invited to the channel

    Exceptions:
        InputError - Occurs when c_id does not refer to a valid channel
        InputError - Occurs when u_id does not refer to a valid user
        InputError - Occurs when u_id refers to a user already in the channel
        AccessError - Occurs when c_id DOES refer to a valid channel, but the authorised user is not in the channel

    Return Value:
        {   }
    '''
    # Calls helper function to check validity of the auth_user and invited user's permissions
    channel = channel_invite_check(auth_u_id, c_id, u_id)
    invitee_user = get_user_info(auth_u_id)
    create_noti(u_id, 3, invitee_user['user_handle'], channel['name'], c_id = channel['id'])

    # Adds user to the members list if valid
    channel['member'].append(u_id)
    
    user_stat_update(u_id, 1, 1)
    update_storage(store)
    return {}


def channel_leave(u_id, c_id):

    '''
    Given a channel with ID channel_id that the authorised user is a member of, 
    remove them as a member of the channel. Their messages should remain in the channel. 
    If the only channel owner leaves, the channel will remain.
    
    Arguments:
        c_id (integer) - the ID of an existing channel
        u_id (integer) - the ID of the user to be invited to the channel

    Exceptions:
        InputError - channel_id does not refer to a valid channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel
      
    Return Value:
        {}
    
    '''
    
    channel = channel_user_check(u_id, c_id)
    for standup in store['standups']:
        if c_id == standup['c_id'] and u_id == standup['u_id']:
            raise InputError(description = 'User cannot leave if they initiated an ongoing standup in the channel')

    if u_id in channel['owner']:
        channel['owner'].remove(u_id)
    channel['member'].remove(u_id)

    user_stat_update(u_id, 1, (-1))
    update_storage(store)
    return {}


def channel_add_owner(auth_u_id, u_id, c_id):
    
    '''
    Make user with user id u_id an owner of the channel.
    
    Arguments:
        c_id (integer) - the ID of an existing channel
        u_id (integer) - the ID of the user to be invited to the channel
        auth_u_id (integer) - the ID of the authorised user - caller of function

    Exceptions:
        InputError - channel_id does not refer to a valid channel
        InputError - u_id does not refer to a valid user
        InputError - u_id refers to a user who is not a member of the channel
        InputError - u_id refers to a user who is already an owner of the channel
        AccessError - channel_id is valid and the authorised user does not have owner permissions in the channel
      
    Return Value:
        {}
    
    '''

    channel = channel_owner_related_check(auth_u_id, u_id, c_id, 1)
    channel['owner'].append(u_id)
    update_storage(store)
    return {}


def channel_remove_owner(auth_u_id, u_id, c_id):

    '''
    Given a channel with ID channel_id that the authorised user is a member of, 
    remove them as a member of the channel. Their messages should remain in the channel. 
    If the only channel owner leaves, the channel will remain.
    
    Arguments:
        c_id (integer) - the ID of an existing channel
        u_id (integer) - the ID of the user to be invited to the channel
        auth_u_id (integer) - the ID of the authorised user - the caller of function

    Exceptions:
        InputError - channel_id does not refer to a valid channel
        InputError - u_id does not refer to a valid user
        InputError - u_id refers to a user who is not an owner of the channel
        InputError - u_id refers to a user who is currently the only owner of the channel 
        AccessError - channel_id is valid and the authorised user does not have owner permissions in the channel
      
    Return Value:
        {}
    
    '''

    channel = channel_owner_related_check(auth_u_id, u_id, c_id, 0)
    channel['owner'].remove(u_id)
    update_storage(store)
    return {}


def channel_messages_v1(auth_u_id, c_id, start):
    '''
    This returns up to 50 messages between the two indexes “start” and "end" (start + 50) 
    from a channel in which the authorised user is a member

    Arguments:
        auth_u_id (integer) - ID of the authorised user
        c_id (integer) - ID of a valid channel
        start (integer) - the starting index of a list of messages

    Exceptions:
        InputError - Occurs when c_id does not refer to a valid channel
        InputError - Occurs when start is greater than the total amount of messages in the channel
        AccessError - Occurs when the authorised user is not a member of the channel
        and the c_id is valid.

    Return Value:
        Returns a list of messages
        Returns an integer called start, which is the index of the first message
        Returns an integer called end, which is the index of start + 50, or -1 if start + 50 exceeds 
        the number of messages in the channel
    '''
    # Message list
    m_list = []
    # Check if user has permissions to access message logs in the current channel
    m_list = channel_messages_check(auth_u_id, c_id, start)

    # Total message length of channel
    t_m_length = len(m_list)  # t_m = total message
    end = start + 50

    return_list = []
    # If the end length is longer than total, it will default to return entire message chain
    if end >= t_m_length:
        end = t_m_length
    for index in range(start, end):
        return_list.append(m_list[index])
    # If end = length, start from end of message chain
    if end == t_m_length:
        end = -1

    # Returns list of messages starting from index 'Start', starting with the most recent
    return {
        'messages': return_list,
        'start': start,
        'end': end,
    }
