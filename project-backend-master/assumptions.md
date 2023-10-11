Data = [ [User data], [Channel data], [tokens] ]

User dictionary structure:{
    'id':,
    'email':,
    'password':,
    # short for first_name
    'f_name':,
    # short for last_name
    'l_name':,
    'user_handle':
    #  simplify for process number in user_handle
    'handle_addon':
}

Channel dictionary structure:{
    'id': 0,
    'name': '',
    'owner': [],
    'member': [],
    'is_public':,
    'message': []
}

tokens dictionary structure:{
    'token': ,
    'auth_user_id': ,
}

Message dictionary structure:{
    'message_id': ,
    'u_id': ,
    'message': '',
    'time_created': TIMESTAMP,
}

Arguments:
    'c' is short for channel
    'u' is short for user

Case Assumptions:
    # Based on assignment specification, the message list is inserted inversly
    # Assume there will be no 2 name entries where names are same for up to the first 20 characters, but different for the remaining characters