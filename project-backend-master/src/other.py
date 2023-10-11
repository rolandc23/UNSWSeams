import re, json, hashlib, os, shutil, jwt
from src.data_store import data_store
from src.error import AccessError, InputError
from datetime import datetime


global store, session_counter
store = data_store.get()
session_counter = 0
TOKEN_KEY = 'Ranni_the_Witch' # super spooky
# IMPORTANT: Every Change in data_store needed to be stored in local storage
def update_storage(data):
    with open('data_store.json','w') as database:
        json.dump(data, database)


def clear_v1():
    '''
    This function clears all internal data in data_store.py to its original empty state.
    It has no parameters, exceptions or returns.
    '''
    cur_time = int(datetime.now().timestamp())
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['sessions'] = []
    store['dms'] = []
    store['messages'] = []
    store['notifications'] = []
    store['standups'] = []
    store['user_stats'] = []
    store['seam_stats'] = {
        'channels_exist': [{'num_channels_exist': 0,
                            'time_stamp': cur_time}], 
        'dms_exist': [{'num_dms_exist': 0,
                            'time_stamp': cur_time}], 
        'messages_exist': [{'num_messages_exist': 0, 
                            'time_stamp': cur_time}], 
        'utilization_rate': 0,
    }
    global session_counter
    session_counter = 0
    data_store.set(store)
    update_storage(store)
    folder_path = os.getcwd()+'/userImage'
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


#################### HELPER FUNCTIONS BELOW #####################



def valid_token_check(token):
    payload = token_decode(token)
    if not any(session_dict == payload for session_dict in store['sessions']):
        # raise AccessError
        raise AccessError(description = 'Invalid user token')
    return payload
 

# Checks if ID is registered in the user dictionary
# Raise InputError (CHANGED FROM iteration 1)
def valid_auth_id_check(auth_user_id):
    if not any(user['id'] == auth_user_id for user in store['users']):
        raise InputError(description = 'Invalid user ID')


# decodes token using given token key
def token_decode(input_token):
    try:
        return jwt.decode(input_token, TOKEN_KEY, algorithms = 'HS256')
    except Exception as e:
        raise AccessError('Invalid Token Signature') from e
    # raise AccessError


def password_encrypt(password):
    secured_pw = hashlib.sha3_256(password.encode())
    return secured_pw.hexdigest()


def session_token_create(dict_type_id, session_id):
    # generates dictionary which contains session_id 
    session_dict = {
        **dict_type_id,
        **{'Session_id': session_id}
    }
    store['sessions'].append(session_dict)
    update_storage(store)
    global session_counter
    # updates counter for number of user sessions in use
    session_counter += 1
    #  generates token
    token = jwt.encode(session_dict, TOKEN_KEY, algorithm = 'HS256')
    return token


# generates token
# creates a dictionary containing token and dictionary of auth users
def token_dict_create(dict_of_auth):
    session_token = session_token_create(dict_of_auth, session_counter)
    login_dict = { 
        **{'token': session_token}, 
        **dict_of_auth,
    }
    return login_dict


# Because tokens can't be duplicated, using for loop and remove
# can work in this case. It's not allowed in general
def session_delete(payload):
    store['sessions'].remove(payload)
    update_storage(store)


# returns a list of dictionaries containing user information for all users.
def get_user_all():
    user_list = []
    for user in store['users']:
        if user['perm_id'] != 0:
            tmp_user = {
                'u_id': user['id'],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['user_handle'],
                'profile_img_url': user['profile_img_url']
            }
            user_list.append(tmp_user)
    return {'users': user_list}


# Both create user / change name using this
def name_check(name_first, name_last):
    # Invalid first name
    if not (len(name_first) > 0 and len(name_first) < 51):
        raise InputError(description = 'length of name is invalid')

    # Invalid last name
    if not (len(name_last) > 0 and len(name_last) < 51):
        raise InputError(description = 'length of name is invalid')


# Both create user / change emial using this
def email_check(email):
    # Checks invalid cases of email address
    reg = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.fullmatch(reg, email):
        raise InputError(description = 'Invalid Email address')
    # Check whether email is used
    if any(user['email'] == email for user in store['users']):
        raise InputError(description = 'Email is already being used')


# Both create user / change password using this
def pw_check(pw):
    # If password is invalid
    if len(pw) < 6:
        raise InputError(description = 'Password is less than 6 characters')


def change_handle_check(input_handle):
    if len(input_handle) < 3 or len(input_handle) > 20:
        raise InputError(description = 'Invalid length of Handle')
    if input_handle.isalnum():
        for user in store['users']:
            if user['user_handle'] == input_handle:
                raise InputError(description = 'Handle is already used by another user')
    else:
        raise InputError(description = 'Handle contains Non-alphanumeric characters')


# Searches channel dictionary, returns channel if exists
def get_channel_info(c_id):
    for channel in store['channels']:
        if channel['id'] == c_id:
            return channel
    raise InputError(description = 'Channel does not exist')


# Searches user dictionary, returns user if exists
def get_user_info(u_id):
    for user in store['users']:
        if user['id'] == u_id:
            return user
    raise InputError(description = 'u_id refer to an invalid user')


def create_m_id():
    if store['messages']:
        m_id = max(message['m_id'] for message in store['messages']) + 1
        return m_id
    # If message is first to be sent
    else:
        return 0

def store_message(message):
    if store['messages']:
        store['messages'] = [message] + store['messages']
    # If message is first to be sent
    else:
        store['messages'].append(message)




# Searches messages list with m_id, returns message if exists
def get_message_info(m_id):
    for message in store['messages']:
        if message['m_id'] == m_id:
            return message
    raise InputError(description = 'Message ID is invalid')


# Searches dm list with m_id, returns dm if exists
def get_dm_info(dm_id):
    for dm in store['dms']:
        if dm['id'] == dm_id:
            return dm
    raise InputError(description = 'dm_id does not refer to valid DM')


# Gets info of list of users with their ID
def get_lists_user_info(u_id_list):

    '''
    Returns a list of all users and their associated details.

    Arguments:
        token (str) - JWT containing { u_id, session_id }

    Exceptions:
        N/A

    Return Value:
        returns a list called 'info_list' of dictionaries which contains the user info for all users

    '''
    # Empty list
    info_list = []
    
    for u_id in u_id_list:
        user = get_user_info(u_id)
        # Create a temporary copy of original user dictionary
        tmp_user = {
            'u_id': user['id'],
            'email': user['email'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'handle_str': user['user_handle'],
            'profile_img_url': user['profile_img_url']
        }
        info_list.append(tmp_user)
    return info_list


def set_is_user_reacted(message, auth_u_id):
    is_reacted = False
    tmp_list = []
    for react in message['reacts']:
        if auth_u_id in react['u_ids']:
            is_reacted = True
        tmp_list.append({
            **react,
            **{'is_this_user_reacted': is_reacted}, 
        })
    return tmp_list

def user_remove_session(u_id):
    new_session_list = []
    for session in store['sessions']:
        if session['auth_user_id'] != u_id:
            new_session_list.append(session)
    store['sessions'] = new_session_list


def stat_analysis(key1, key2, key3, dict_of_stat):
    subkey = 'num_'
    return (dict_of_stat[key1][-1][subkey+key1] +
                dict_of_stat[key2][-1][subkey+key2] +
                dict_of_stat[key3][-1][subkey+key3])
