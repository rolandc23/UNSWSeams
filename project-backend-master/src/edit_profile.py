from src.data_store import data_store
from src.other import update_storage

global store
store = data_store.get()

# given new first and last name, overwrites existing names
def change_name(u_id, name_first, name_last):

    '''
    
    Update the authorised user's first and last name  

    Arguments:
        u_id - the user id
        name_first (str) - the desired new first name
        name_last (str) - the desired new last name

    Exceptions:
        InputError - length of name_first is not between 1 and 50 characters inclusive
        InputError - length of name_last is not between 1 and 50 characters inclusive

    Return Value:
        N/A
        
    '''
    for user in store['users']: # pragma: no branch
        if user['id'] == u_id:
            user['name_first'] = name_first
            user['name_last'] = name_last
            update_storage(store)
            break
    return {}

# given new email, overwrites old email
def change_email(u_id, email):
    '''
    Update the authorised user's email address

    Arguments:
        u_id - the user id
        email (str) - the desired new email

    Exceptions:
        InputError - email entered is not a valid email (more in section 6.4)
        InputError - email address is already being used by another user

    Return Value:
        N/A
    '''
    for user in store['users']: # pragma: no branch
        if user['id'] == u_id:
            user['email'] = email
            update_storage(store)
            break
    return {}


# given new user handle, overwrites old user handle
def change_handle(u_id, handle):
    '''
    Update the authorised user's handle (i.e. display name)

    Arguments:
        u_id - the user id
        handle (str) - the desired new user handle

    Exceptions:
        InputError - length of handle_str is not between 3 and 20 characters inclusive
        InputError - handle_str contains characters that are not alphanumeric
        InputError - the handle is already used by another user

    Return Value:
        N/A

    '''
    for user in store['users']:  # pragma: no branch
        if user['id'] == u_id:
            user['user_handle'] = handle
            user['handle_string'] = handle
            user['handle_addon'] = None
            update_storage(store)
            break
    return {}        
