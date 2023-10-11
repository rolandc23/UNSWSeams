from src.data_store import data_store
from src.error import InputError
from src.other import name_check, email_check, pw_check, password_encrypt, update_storage
from src.config import url
from src.user_stats import user_stat_init
import re

global store
store = data_store.get()

# Helper functions below

# Helper function for creating user handle
def check_exist_handle(tmp_handle):
    input_addon = re.search(r'\d+\Z',tmp_handle)
    if input_addon:
        input_addon = int(input_addon.group(0))
        tmp_handle = re.sub(r'\d+\Z', '', tmp_handle)
    add_on_list = []
    for user in store['users']:
        # If exact string part of handle already exists
        if user['handle_string'] == tmp_handle:
            add_on_list.append(user['handle_addon'])
    if add_on_list and None in add_on_list:
        addon = 0
        while True:
            if addon not in add_on_list:
                break
            addon += 1
        if input_addon and input_addon > addon:
            addon = input_addon
        return addon
    return input_addon

# Helper function for creating user handle
def create_user_handle(name_first, name_last):
    # Generates user handles by concatenating lowercase first and last names with addon in case of duplicates
    tmp_first = re.sub(r'[^a-zA-z0-9]', '', name_first)
    tmp_last = re.sub(r'[^a-zA-z0-9]', '', name_last)
    if len(tmp_first) <= 0 or len(tmp_last) <= 0:
        raise InputError(description = 'Invalid name after removing symbol')
    tmp_first = tmp_first.lower()
    tmp_last = tmp_last.lower()
    tmp_full = tmp_first + tmp_last

    # If name length is greater than 20, only include first 20 characters
    if len(tmp_full) > 20:
        tmp_full = tmp_full[:20]

    # Check if number addon is required
    num_addon = check_exist_handle(tmp_full)
    tmp_full = re.sub(r'\d+\Z', '', tmp_full)

    # Returns user handle string part and its numerical addon
    return tmp_full, num_addon


def create_new_user(email, password, name_first, name_last):
    handle_string, addon = create_user_handle(name_first, name_last)
    if addon is None:
        user_handle = handle_string
    else:
        user_handle = handle_string + str(addon)
    # create and initialises the dictionary data structure for users
    user = {
        'id': 0,
        'email': email,
        'password': password,
        'reset_code': '',
        'name_first': name_first,
        'name_last': name_last,
        'user_handle':  user_handle,
        'handle_string': handle_string,
        'handle_addon': addon,
        'profile_img_url': f'{url}profileAvatar/default',
        # default seams permission set to 1: means owner
        'perm_id': 1,
    }

    u_id = 0
    # If store['users'] is not an empty list:
    if store['users']:
        u_id = max(user['id'] for user in store['users']) + 1
        user['perm_id'] = 2
    user['id'] = u_id
    return user


# Main functions below 

def auth_register_v1(email, password, name_first, name_last):
    '''
    This function allows a user to register an account. It then assigns them a user id

    Arguments: 
        email (string) - New user's email
        password (string) - User's desired password  
        name_first (string) - User's first name
        name_last (string) - User's last name

    Exceptions:
        InputError - Occurs when the email entered is not a valid email
        InputError - Occurs when the email entered has already been registered
        InputError - Occurs when the password entered is less than 6 characters long
        InputError - Occurs when the first name is not between 1 and 50 characters inclusive
        InputError - Occurs when the last name is not between 1 and 50 characters inclusive

    Return Value: 
        Returns a new auth_user_id for its corresponding user email
    '''
    email_check(email)
    pw_check(password)
    name_check(name_first, name_last)

    password = password_encrypt(password)
    user = create_new_user(email, password, name_first, name_last)
    store['users'].append(user)  # stores new users in dictionary
    user_stat_init(user['id'])
    update_storage(store)
    return {'auth_user_id': user['id']}


def auth_login_v1(email, password):
    '''
    This function allows registered users to login to their account if they enter the correct password

    Arguments: 
        email (string) - Registered user email 
        password (string) - Correct password

    Exceptions:
        InputError - Occurs when the email is not registered
        InputError - Occurs when the entered password is not correct

    Return Value: 
        Returns u_id if the correct password is entered for the corresponding email
    '''
    reg = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.fullmatch(reg, email):
        raise InputError(description = 'Invalid Email address')
    for user in store['users']:
        if user['email'] == email:
            if user['reset_code']:
                raise InputError(description = 'Requested password reset. Please set new password')
            # If password is valid
            if user['password'] == password:
                return {'auth_user_id': user['id']}

            # Password not valid
            raise InputError(description = 'Invalid password')

    # If email isn't registered
    raise InputError(description = 'Email is not registered')