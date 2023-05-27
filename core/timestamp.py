import datetime

def get_current_timestamp():
    ct = datetime.datetime.now()
    ts = ct.timestamp()
    return ts