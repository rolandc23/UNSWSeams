from src.error import InputError
from src.data_store import data_store
from src.other import update_storage
from src.user_stats import user_stat_update
from src.seam_stats import sys_stat_update

global store
store = data_store.get()


# DO NOT return channel data if u_id is invalid, otherwise display channels which user is currently in
def channels_list_v1(auth_user_id):
    '''
    This function allows an authorised user to see a list containing currently existing channels to which they belong
    
    Arguments:
        auth_user_id (integer) - ID of the authorised user

    Exceptions:
        NONE

    Return Value:
        Returns a list of the channels to which they belong, as well as channel details
    '''

    # Creates empty list of channels to populate
    result_list = []

    # Checks which channels user is a member of
    for channel in store['channels']:
        # for user's channels, appends them into result_list
        if auth_user_id in channel['member']:
            result_list.append(
                {
                    'channel_id': channel['id'],
                    'name': channel['name']
                }
            )

    # Returns the populated list with channel names and respective IDs
    return {'channels': result_list}


# DO NOT return channel data if u_id is invalid, otherwise display all channels
def channels_listall_v1():

    '''
    This function allows an authorised user to see a list containing all currently existing channels
    
    Arguments:
        None -- As token checked by server.py

    Exceptions:
        NONE

    Return Value:
        Returns a list of all channels and their details
    '''

    # Empty list
    result_list = []

    # Loops through all channels in channel dictionary and appends ID + name of channel to result
    for channel in store['channels']:
        result_list.append(
            {
                'channel_id': channel['id'],
                'name': channel['name']
            }
        )

    # Return channel ID + name
    return {'channels': result_list}


def channels_create_v1(auth_user_id, name, is_public):
    '''
    This function allows an authorised user to create a channel. This involves choosing its name and privacy setting

    Arguments:
        auth_user_id (integer) - ID of the authorised user
        name (string) - The channel's name, chosen by the authorised user
        is_public (boolean) - The channel's privacy setting, chosen by the authorised user

    Exceptions:
        InputError - Occurs when the channel name is less than 1 character or more than 20 characters

    Return Value:
        Returns a channel id
    '''
    
    # Check if name of channel is valid
    channels_create_check(name)
    channel = {
        'id': 0,
        'name': name,
        'owner': [],
        'member': [],
        'is_public': is_public, # is_public is boolean type
    }

    # Same procedure as create ID for users
    c_id = 0

    # If channels is not an empty list
    if store['channels']:
        c_id = max(channel['id'] for channel in store['channels']) + 1
    channel['id'] = c_id
    channel['owner'].append(auth_user_id)
    channel['member'].append(auth_user_id)
    store['channels'].append(channel)

    user_stat_update(auth_user_id, 1, 1)
    sys_stat_update(1, 1)
    update_storage(store)
    # Returns ID of channel created
    return {'channel_id': channel['id']}


# Helper funtions below
# Checks the validity of the channel name
def channels_create_check(name):
    if len(name) < 1 or len(name) > 20:
        raise InputError(description = 'Invalid length of name for channel')
