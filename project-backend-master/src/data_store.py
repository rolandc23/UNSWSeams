'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''
import json, os
from datetime import datetime
## YOU SHOULD MODIFY THIS OBJECT BELOW
cur_time = int(datetime.now().timestamp())
initial_object = {
    'users': [],
    # add channels
    'channels': [],
    # add dms
    'dms': [],
    # add sessions
    'sessions': [],
    # add messages
    'messages': [],
    # add notifications
    'notifications': [],
    # add standups
    'standups': [],
    # add user_stats
    'user_stats': [],
    # add seams stats
    'seam_stats': {
        'channels_exist': [{'num_channels_exist': 0,
                            'time_stamp': cur_time}], 
        'dms_exist': [{'num_dms_exist': 0,
                            'time_stamp': cur_time}], 
        'messages_exist': [{'num_messages_exist': 0, 
                            'time_stamp': cur_time}], 
        'utilization_rate': 0,
    },
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

## YOU ARE ALLOWED TO CHANGE THE BELOW IF YOU WISH
class Datastore:
    def __init__(self):
        # check local storage exist and permission to read & write storage file
        if os.path.isfile('data_store.json') and os.access('data_store.json', os.R_OK & os.W_OK):
            with open('data_store.json','r') as database:
                self.__store = json.load(database)
        else:
            # do not have local storage, initialize variable and create file to store
            self.__store = initial_object
            with open('data_store.json','w') as database:
                json.dump(self.__store, database)

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()
