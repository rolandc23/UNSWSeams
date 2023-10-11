from src.data_store import data_store
from src.other import update_storage, stat_analysis
from datetime import datetime

global store
store = data_store.get()


# 1. function which updates a list of channels with a time when joining
# 2. function which updates number of channels joined with timestamp


# Dictionary of shape {
#      u_id: 0,
#      channels_joined: [
#               {
#               num_channels_joined : 0, 
#               time_stamp :
#               }

#               {
#               num_channels_joined : 1, 
#               time_stamp :
#               }
#           ],
#      dms_joined: [{num_dms_joined, time_stamp}], 
#      messages_sent: [{num_messages_sent, time_stamp}], 

#      involvement_rate 
#     }


# when a user just register his account
def user_stat_init(u_id):
    cur_time = int(datetime.now().timestamp())
    stat_dict = {
        'u_id': u_id,
        'channels_joined': [{
            'num_channels_joined': 0,
            'time_stamp': cur_time
        }],
        'dms_joined': [{
            'num_dms_joined': 0,
            'time_stamp': cur_time
        }],
        'messages_sent': [{
            'num_messages_sent': 0,
            'time_stamp': cur_time
        }],
        'involvement_rate': 0,
    }
    store['user_stats'].append(stat_dict)
    

# operation indicates for join/left channel/dm. message will only increase
def user_stat_update(u_id, mode, operation):
    key = ''
    if mode == 1:
        key = 'channels_joined'
    elif mode == 2:
        key = 'dms_joined'
    else:
        key = 'messages_sent'
    sub_key = 'num_'+key
    for user_stat in store['user_stats']:
        if user_stat['u_id'] == u_id:
            sub_dict = {}
            sub_dict[sub_key] = user_stat[key][-1][sub_key] + operation
            sub_dict['time_stamp'] = int(datetime.now().timestamp())
            user_stat[key].append(sub_dict)
            


def get_user_stat_obj(u_id):
    for user_stat in store['user_stats']: # pragma: no branch
        if user_stat['u_id'] == u_id:
            return user_stat


def get_user_stats(u_id):
   
    user_stat = get_user_stat_obj(u_id)
    sys_stat = store['seam_stats']

    user_involvement = stat_analysis('channels_joined', 'dms_joined', 'messages_sent', user_stat)
    seams_workspace = stat_analysis('channels_exist', 'dms_exist', 'messages_exist', sys_stat)
    
    involvment_rate = 0
    if seams_workspace:
        tmp_rate = user_involvement/seams_workspace
        involvment_rate = tmp_rate if tmp_rate < 1 else 1

    user_stat['involvement_rate'] = involvment_rate
    update_storage(store)
    
    dict_key = ['channels_joined','dms_joined','messages_sent','involvement_rate']
    tmp_dict = {key: user_stat[key] for key in dict_key}
    return {'user_stats': tmp_dict}
