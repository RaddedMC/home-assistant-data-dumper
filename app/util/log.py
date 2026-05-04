import datetime
from . import placeholders

def error(msg):
    __log__(msg, "ERROR")

def warning(msg):
    __log__(msg, "WARNING")

def info(msg):
    __log__(msg, "INFO")
    
def toomuchinfo(msg):
    __log__(msg, "TMI")

def __log__(msg, status):
    print(f"radded_data_dumper: [{status}] @ {str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))} : {msg}")