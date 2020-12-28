import datetime, os
import app.settings as settings

def get_number_input(msg_prompt):
    while True:
        user_input = input(msg_prompt)
        if user_input.isnumeric():
            return user_input
        else:
            print('Input Not Understood. Please Enter A Numerical Value.')

def get_first_json_key(this_json):
    return list(this_json.keys())[0]


def clear_cache():
    now = datetime.datetime.now()
    filelist = [ f for f in os.listdir(settings.CACHE_DIR)]
    timestamp = '{}{}{}'.format(now.month, now.day, now.year)
    for f in filelist:
        filename = os.path.basename(f)
        if filename != ".gitkeep" and timestamp not in filename:
            os.remove(os.path.join(settings.CACHE_DIR, f))

def clear_static():
    filelist = [ f for f in os.listdir(settings.STATIC_DIR)]
    for f in filelist:
        os.remove(f)