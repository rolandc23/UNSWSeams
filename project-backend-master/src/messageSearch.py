from src.data_store import data_store
from src.error import InputError
from src.other import get_channel_info, get_dm_info

store = data_store.get()


def search_v1(u_id, query_str):

    query_len = len(query_str)
    if query_len < 1 or query_len > 1000:
        raise InputError(description = 'length of query_str is invalid') 

    m_list = []
    c_dm_obj = None
    query_str = query_str.lower()

    for message in store['messages']:
        if query_str in message['message'].lower():
            if message['is_DM']:
                c_dm_obj = get_dm_info(message['dm_id'])
            else:
                c_dm_obj = get_channel_info(message['c_id'])
            if u_id in c_dm_obj['member']:
                m_list.append(message['message'])

    return {'messages': m_list}         
