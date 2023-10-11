from src.data_store import data_store
from src.other import update_storage

global store
store = data_store.get()


def get_noti(u_id):
    return_list = []
    keys = ['channel_id', 'dm_id', 'notification_message']
    count = 0
    for notification in store['notifications']:
        if notification['u_id'] == u_id and count < 20:
            tmp = {key:notification[key] for key in keys if key in notification}
            return_list.append(tmp)
            count += 1
    return {'notifications': return_list}


def create_noti(u_id, noti_type, user_handle, c_dm_name, c_id = -1, dm_id = -1, noti_message =''):
    # u_id is who receive the notification
    # noti type == 1: someone tagged
    # noti type == 2: reacted message
    # noti type == 3: someone added you to channel
    tmp_noti = {
        'u_id': u_id,
        'channel_id': c_id,
        'dm_id': dm_id, 
        'notification_message': '',
    }
    if noti_type == 1:
        noti_str = f'{user_handle} tagged you in {c_dm_name}: {noti_message}'
    elif noti_type == 2:
        noti_str = f'{user_handle} reacted to your message in {c_dm_name}'
    else:
        noti_str = f'{user_handle} added you to {c_dm_name}'
    
    tmp_noti['notification_message'] = noti_str
    store['notifications'] = [tmp_noti] + store['notifications']
    update_storage(store)