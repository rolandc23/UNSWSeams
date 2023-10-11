from src.data_store import data_store
from src.other import update_storage
from datetime import datetime

global store
store = data_store.get()

# operation indicates for join/left channel/dm. message will only increase
def sys_stat_update(mode, operation):
    key = ''
    if mode == 1:
        key = 'channels_exist'
    elif mode == 2:
        key = 'dms_exist'
    else:
        key = 'messages_exist'
    sub_key = 'num_'+key

    sys_stat = store['seam_stats'][key]
    sub_dict = {
        sub_key: sys_stat[-1][sub_key] + operation,
        'time_stamp': int(datetime.now().timestamp())
    }

    sys_stat.append(sub_dict)
    


def get_sys_stats ():
   
    active_user_count = 0
    for user_stat in store['user_stats']:
        if user_stat['channels_joined'][-1]['num_channels_joined'] > 0 or user_stat['dms_joined'][-1]['num_dms_joined'] > 0:
            active_user_count += 1

    total_user_count = len(store['users'])

    utili_rate = 0
    if total_user_count:
        utili_rate = active_user_count/total_user_count

    store['seam_stats']['utilization_rate'] = utili_rate
    update_storage(store)

    return {'workspace_stats': store['seam_stats']}
