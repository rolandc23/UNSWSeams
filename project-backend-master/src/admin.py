from src.data_store import data_store
from src.other import get_user_info, update_storage, user_remove_session
from src.error import InputError, AccessError
from src.config import url

store = data_store.get()


def change_user_perm(auth_u_id, u_id, perm_id):

    '''
    Given a user by their user ID, set their permissions to new permissions
    described by permission_id.

    Arguments:
        u_id (int) - users unique id - the target user
        auth_u_id (int) - The ID of the authorised user - the caller
        perm_id (int) - 1 = seams owner permission, 2 = normal user permission, 0 = remove user permission 

    Exceptions:
        InputError -  u_id does not refer to a valid user
        InputError -  u_id refers to a user who is the only global owner and they are being demoted to a user
        InputError -  permission_id is invalid
        InputError -  the user already has the permissions level of permission_id
        AccessError - the authorised user is not a global owner

    Return Value:
        {}
    
    '''
    global_owner = []
    for user in store['users']:
        if user['perm_id'] == 1:
            global_owner.append(user['id'])
    
    if auth_u_id not in global_owner:
        raise AccessError(description = 'authorised user is not a global owner')
    
    user = get_user_info(u_id)

    if perm_id != 1 and perm_id != 2:
        raise InputError(description = 'Invalid permission id')
    
    if user['perm_id'] == perm_id:
        raise InputError(description = 'user already has the permissions level of permission id')

    if user['id'] in global_owner and len(global_owner) == 1:
        raise InputError(description = 'Unable to demote the last global owner')
    
    user['perm_id'] = perm_id
    update_storage(store)
    return {}


def admin_user_remove_v1(auth_u_id, u_id):

    '''
    Given a user by their u_id, remove them from the Seams. This means they should be removed
    from all channels/DMs, and will not be included in the list of users returned by users/all. 
    Seams owners can remove other Seams owners (including the original first owner). 
    Once users are removed, the contents of the messages they sent will be replaced by '
    Removed user'. Their profile must still be retrievable with user/profile, 
    however name_first should be 'Removed' and name_last should be 'user'. The user's email and
    handle should be reusable.

    Arguments:
        u_id - users unique id
        token (str) - JWT containing { u_id, session_id }

    Exceptions:
        InputError -  u_id does not refer to a valid user
        InputError -  u_id refers to a user who is the only global owner

    Return Value:
        {}
    
    '''
    
    target_user = get_user_info(u_id)
    auth_user = get_user_info(auth_u_id)

    global_owner = []
    for user in store['users']:
        if user['perm_id'] == 1:
            global_owner.append(user['id'])

    # Check error cases
    if auth_user['perm_id'] != 1:
        raise AccessError(description = 'Authorised user is not a global owner')
            
    if len(global_owner) == 1:
        if auth_u_id == u_id:
            raise InputError(description = 'Authorised user is the only global owner')

    # Clearing user attributes
    target_user['name_first'] = 'Removed'
    target_user['name_last'] = 'user'
    target_user['email'] = ''
    target_user['password'] = ''
    target_user['user_handle'] = ''
    target_user['handle_string'] = ''
    target_user['perm_id'] = 0
    target_user['profile_img_url'] = f'{url}profileAvatar/default'
    
    # Removing messages sent by user across all channels
    for message in store['messages']:
        if message['creator'] == u_id:
            message['message'] = 'Removed user'

    # Removing user from channels
    for channel in store['channels']:
        if u_id in channel['member']:
            channel['member'].remove(u_id)
            if u_id in channel['owner']:
                channel['owner'].remove(u_id)

    # Removing user from dms
    for dm in store['dms']:
        if u_id in dm['member']:
            dm['member'].remove(u_id)
            if u_id == dm['owner']:
                dm['owner'] = ''

    user_remove_session(u_id)

    new_notification_list = []
    for noti in store['notifications']:
        if noti['u_id'] != u_id:
            new_notification_list.append(noti)
    store['notifications'] = new_notification_list
    
    update_storage(store)

    return {}
