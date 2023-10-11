import os,signal, flask_mail
from json import dumps
from flask import Flask, request, send_file
from flask_cors import CORS
from src import (config, auth, channels, channel, edit_profile,
            message, messageReactTagging, other, admin, data_store, dm, notifications, messageShare,
            profile_photo, messageSearch, password_reset, standup, messagePin, user_stats, seam_stats)
from src.error import InputError

global store
store = data_store.data_store.get()

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)
# Following code from https://pythonbasics.org/flask-mail/ used for flask server sending email
APP.config['MAIL_SERVER']='smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = 'cs1531f11cbadger@gmail.com'
APP.config['MAIL_PASSWORD'] = 'y"5L<LeH383e{]7+'
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
APP.config['MAIL_DEFAULT_SENDER'] = 'cs1531f11cbadger@gmail.com'
mail = flask_mail.Mail(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS


@APP.route("/clear/v1", methods=["DELETE"])
def data_clear():
    other.clear_v1()
    return {}


# Given a registered user's email and password, returns their `auth_user_id` value and a new `token`.
@APP.route("/auth/login/v2", methods=['POST'])
def login():
    data = request.get_json() # returns incoming JSON data
    pw = other.password_encrypt(data['password'])
    login_result = auth.auth_login_v1(data['email'], pw)
    return other.token_dict_create(login_result)


# Given a user's first and last name, email address, and password, 
# create a new account for them and return a new `auth_user_id` and `token`.
@APP.route("/auth/register/v2", methods=['POST'])
def register():
    data = request.get_json()       # returns incoming JSON data
    reg_result = auth.auth_register_v1(data['email'], data['password'], data['name_first'], data['name_last'])       # assigns u_id to user when registering
    return other.token_dict_create(reg_result)      # uses u_id to generate token and place into dictionary


@APP.route("/auth/logout/v1", methods=["POST"])
def logout():
    data = request.get_json()
    payload = other.valid_token_check(data['token'])
    other.session_delete(payload)
    return {}


@APP.route("/auth/passwordreset/request/v1", methods=["POST"])
def request_reset_pw():
    data = request.get_json()
    msg = password_reset.reset_request(data['email'])
    if msg:
        mail.send(msg)
    return {}

@APP.route("/auth/passwordreset/reset/v1", methods=["POST"])
def reset_pw():
    data = request.get_json()
    password_reset.pw_reset(data['reset_code'], data['new_password'])
    return {}


@APP.route("/users/all/v1", methods=['GET'])
def get_all_user():
    token = request.args.get('token')
    other.valid_token_check(token)
    return other.get_user_all()     # converts returned dictionary into JSON object


# For a valid user, returns information about their user_id, email, first name, last name, and handle
@APP.route("/user/profile/v1", methods=['GET'])
def get_single_user():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))        # converts the u_id from type str to int
    other.valid_token_check(token)
    other.valid_auth_id_check(u_id)
    user = other.get_user_info(u_id)        # returns dictionary of a valid user's information from u_id
    return {
        'user': {
            'u_id': user['id'],
            'email': user['email'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'handle_str': user['user_handle'],
            'profile_img_url': user['profile_img_url']
            }
    }


@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_change_name():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']      # checks if given token is valid
    other.name_check(data['name_first'], data['name_last'])        # checks if the changed name is of valid format
    return edit_profile.change_name(u_id, data['name_first'], data['name_last'])
    

# Update the authorised user's email address.
@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_change_email():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']   # checks if given token is valid
    other.email_check(data['email'])        # checks if the changed email is of valid format
    return edit_profile.change_email(u_id, data['email'])


# Update the authorised user's handle (i.e. display name)
@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_change_handle():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']      # checks if given token is valid  
    other.change_handle_check(data['handle_str'])        # checks if the changed user handle is of valid format
    return edit_profile.change_handle(u_id, data['handle_str'])


@APP.route("/user/profile/uploadphoto/v1", methods=["POST"])
def user_upload_avatar():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return profile_photo.upload_profile_image(u_id, data['img_url'],data['x_start'],data['y_start'],
                                            data['x_end'], data['y_end'])


@APP.route("/profileAvatar/default", methods=["GET"])
def return_default_avater():
    filename = os.getcwd() + '/src/default.jpg'
    return send_file(filename)


@APP.route("/profileAvatar", methods=["GET"])
def return_user_avater():
    u_id = int(request.args.get('u_id'))
    curr_path = os.getcwd() + '/userImage'
    filename = f'{curr_path}/{u_id}.jpg'
    try:
        return send_file(filename)
    except Exception as e:
        raise InputError(description= 'User does not set up Avater') from e


@APP.route("/channels/create/v2", methods=["POST"])
def channel_create():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return channels.channels_create_v1(u_id, data['name'], data['is_public'] )


# Provide a list of all channels (and their associated details) that the authorised user is part of.
@APP.route("/channels/list/v2", methods=["GET"])
def channel_list():
    token = request.args.get('token')
    u_id = other.valid_token_check(token)['auth_user_id']
    return channels.channels_list_v1(u_id)


# Provide a list of all channels, including private channels, (and their associated details)
@APP.route("/channels/listall/v2", methods=["GET"])
def channel_list_all():
    token = request.args.get('token')
    other.valid_token_check(token)
    return channels.channels_listall_v1()


# Given a channel with ID channel_id that the authorised user is a member of, 
# provide basic details about the channel.
@APP.route("/channel/details/v2", methods=["GET"])
def channel_detail():
    token = request.args.get('token')
    c_id = int(request.args.get('channel_id'))
    u_id = other.valid_token_check(token)['auth_user_id']
    return channel.channel_details_v1(u_id, c_id)


# Given a channel_id of a channel that the authorised user can join, adds them to that channel.
@APP.route("/channel/join/v2", methods=["POST"])
def channel_join():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return channel.channel_join_v1(u_id, data['channel_id'])


# Invites a user with ID u_id to join a channel with ID channel_id. 
# Once invited, the user is added to the channel immediately. 
# In both public and private channels, all members are able to invite users.
@APP.route("/channel/invite/v2", methods=["POST"])
def channel_invite():
    data = request.get_json()
    user_inviter = other.valid_token_check(data['token'])['auth_user_id']
    user_invitee = int(data['u_id'])
    return channel.channel_invite_v1(user_inviter, data['channel_id'], user_invitee)


# Given a channel with ID channel_id that the authorised user is a member of, 
# return up to 50 messages between index "start" and "start + 50". 
@APP.route("/channel/messages/v2", methods=["GET"])
def get_channel_message():
    token = request.args.get('token')
    c_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    u_id = other.valid_token_check(token)['auth_user_id']
    return channel.channel_messages_v1(u_id, c_id, start)


# Given a channel with ID channel_id that the authorised user is a member of, 
# remove them as a member of the channel. 
@APP.route("/channel/leave/v1", methods=["POST"])
def channel_leave():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return channel.channel_leave(u_id, data['channel_id'])


# Make user with user id u_id an owner of the channel.
@APP.route("/channel/addowner/v1", methods=["POST"])
def add_channel_owner():
    data = request.get_json()
    auth_u_id = other.valid_token_check(data['token'])['auth_user_id']
    return channel.channel_add_owner(auth_u_id, data['u_id'], data['channel_id'])


# Remove user with user id u_id as an owner of the channel.
@APP.route("/channel/removeowner/v1", methods=["POST"])
def remove_channel_owner():
    data = request.get_json()
    auth_u_id = other.valid_token_check(data['token'])['auth_user_id']
    return channel.channel_remove_owner(auth_u_id, data['u_id'], data['channel_id'])


# Send a message with unique id from the authorised user to the channel specified by channel_id. 
@APP.route("/message/send/v1", methods=["POST"])
def send_ch_messages():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return message.send_messages_mix(u_id, data['channel_id'], data['message'], 1)


@APP.route("/message/sendlater/v1", methods=["POST"])
def send_ch_messages_delay():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return message.send_messages_mix(u_id, data['channel_id'], 
                        data['message'], 1, is_delay=True, timestamp= data['time_sent'])


@APP.route("/message/senddm/v1", methods=["POST"])
def send_dm_messages():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return message.send_messages_mix(u_id, data['dm_id'], data['message'], 2)


@APP.route("/message/sendlaterdm/v1", methods=["POST"])
def send_dm_messages_delay():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return message.send_messages_mix(u_id, data['dm_id'], 
                        data['message'], 2, is_delay=True, timestamp= data['time_sent'])


# Given a message, update its text with new text. If the new message is an empty string, the message is deleted.
@APP.route("/message/edit/v1", methods=["PUT"])
def edit_messages():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    message.edit_message(data['message'], data['message_id'], u_id)
    return {}


@APP.route("/message/remove/v1", methods=["DELETE"])
def remove_messages():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    message.remove_message(data['message_id'], u_id)
    return {}


@APP.route("/dm/create/v1", methods=["POST"])
def create_dm():
    data = request.get_json()
    owner_id = other.valid_token_check(data['token'])['auth_user_id']
    user_list = data['u_ids']
    return dm.dm_create(user_list, owner_id)


@APP.route("/dm/list/v1", methods=["GET"])
def dm_list():
    token = request.args.get('token')
    u_id = other.valid_token_check(token)['auth_user_id']
    return dm.dm_list_v1(u_id)


@APP.route("/dm/remove/v1", methods=["DELETE"])
def dm_remove():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return dm.dm_remove_v1(data['dm_id'], u_id)


@APP.route("/dm/details/v1", methods=["GET"])
def dm_details():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    u_id = other.valid_token_check(token)['auth_user_id']
    return dm.dm_details_v1(dm_id, u_id)


@APP.route("/dm/leave/v1", methods=["POST"])
def dm_leave():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return dm.dm_leave_v1(data['dm_id'], u_id)


@APP.route("/dm/messages/v1", methods=["GET"])
def get_dm_message():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))
    u_id = other.valid_token_check(token)['auth_user_id']
    return dm.dm_messages_v1(u_id, dm_id, start)


# Given a user by their u_id, remove them from the Seams (all channels/DMs). 
@APP.route("/admin/user/remove/v1", methods=["DELETE"])
def admin_user_remove():
    data = request.get_json()
    auth_u_id = other.valid_token_check(data['token'])['auth_user_id']
    other.valid_auth_id_check(data['u_id'])
    admin.admin_user_remove_v1(auth_u_id, data['u_id'])
    return {}


# Given a user by their user ID, set their permissions to new permissions described by permission_id.
@APP.route("/admin/userpermission/change/v1", methods=["POST"])
def admin_change_perm():
    data = request.get_json()
    auth_u_id = other.valid_token_check(data['token'])['auth_user_id']
    return admin.change_user_perm(auth_u_id, data['u_id'], data['permission_id'])


@APP.route("/notifications/get/v1", methods=["GET"])
def get_notifications():
    token = request.args.get('token')
    u_id = other.valid_token_check(token)['auth_user_id']
    return notifications.get_noti(u_id)


@APP.route("/message/react/v1", methods=["POST"])
def message_react():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return messageReactTagging.message_react(u_id, data['message_id'], data['react_id'])


@APP.route("/message/unreact/v1", methods=["POST"])
def message_unreact():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return messageReactTagging.message_unreact(u_id, data['message_id'], data['react_id'])


@APP.route("/message/share/v1",methods=["POST"])
def message_share():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return messageShare.message_share(u_id, data['og_message_id'], data['channel_id'], data['dm_id'], data['message'])


@APP.route("/search/v1", methods=["GET"])
def search_message_v1():
    token = request.args.get('token')
    u_id = other.valid_token_check(token)['auth_user_id']
    query_str = request.args.get('query_str')
    return messageSearch.search_v1(u_id, query_str)


@APP.route("/message/pin/v1",methods=["POST"])
def message_pin():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return messagePin.message_pin_v1(u_id, data['message_id'], 1)

@APP.route("/message/unpin/v1",methods=["POST"])
def message_unpin():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return messagePin.message_pin_v1(u_id, data['message_id'], 0)


@APP.route("/standup/start/v1", methods = ["POST"])
def standup_start():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return standup.standup_start_v1(u_id, data['channel_id'], data['length'])


@APP.route("/standup/active/v1", methods = ["GET"])
def standup_active():
    token = request.args.get('token')
    u_id = other.valid_token_check(token)['auth_user_id']
    c_id = int(request.args.get('channel_id'))
    return standup.standup_active_v1(u_id, c_id)


@APP.route("/standup/send/v1", methods = ["POST"])
def standup_send():
    data = request.get_json()
    u_id = other.valid_token_check(data['token'])['auth_user_id']
    return standup.standup_send_v1(u_id, data['channel_id'], data['message'])


@APP.route("/user/stats/v1",methods=["GET"])
def user_stats_info():
    token = request.args.get('token')
    u_id = other.valid_token_check(token)['auth_user_id']
    return user_stats.get_user_stats(u_id) 


@APP.route("/users/stats/v1",methods=["GET"])
def users_stats_info():
    token = request.args.get('token')
    other.valid_token_check(token)
    return seam_stats.get_sys_stats()


#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage

    APP.run(port=config.port, debug=False) # Do not edit this port
