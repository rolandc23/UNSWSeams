import random, string, flask_mail
from src.data_store import data_store
from src.other import update_storage, pw_check, user_remove_session, password_encrypt
from src.error import InputError

store = data_store.get()

def generate_reset_code():
    reset_code = ''.join([random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(10)])
    return reset_code


def reset_request(email):
    for user in store['users']:
        if user['email'] == email:
            u_id = user['id']
            origin_code = generate_reset_code()
            reset_code = password_encrypt(origin_code)
            user['reset_code'] = reset_code 
            user['password'] = ''  
            msg = flask_mail.Message(subject='Code for password reset', 
                                    recipients=[email], body = origin_code)
            msg.add_recipient('cs1531f11cbadger@gmail.com')
            user_remove_session(u_id)
            update_storage(store)
            return msg
    return None


def pw_reset(input_code, new_password): # pragma: no cover
    reset_code = password_encrypt(input_code)
    for user in store['users']:
        if user['reset_code'] == reset_code:
            pw_check(new_password)
            user['password'] = password_encrypt(new_password)
            user['reset_code'] = ''
            update_storage(store)
            return {}
    raise InputError(description= 'Invalid reset code')