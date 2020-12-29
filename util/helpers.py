import datetime, os, io, json, csv, zipfile
import requests
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

def replace_troublesome_chars(msg):
    return msg.replace('\u2265','').replace('\u0142', '')

def parse_csv_response_column(column, url, firstRowHeader=None, savefile=None, zipped=None):
     with requests.Session() as s:
        download = s.get(url)
        
        if zipped is not None:
            zipdata = io.BytesIO(download.content)
            unzipped = zipfile.ZipFile(zipdata)
            with unzipped.open(zipped, 'r') as f:
                big_mother=[]
                for line in f:
                    big_mother.append(replace_troublesome_chars(line.decode("utf-8")))

                cr = csv.reader(big_mother, delimiter=',')
        
        else:
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')

        s.close()
        col = []
        for row in cr:
            if row[column] != firstRowHeader:
                col.append(row[column])

        if savefile is not None:    
            with open(savefile, 'w') as outfile:
                json.dump(col, outfile)

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