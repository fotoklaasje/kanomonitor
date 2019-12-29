import sqlite3
import time
from datetime import datetime

x="1"
while (x=="1"):
    print(str(datetime.now()))
    conn_ramdisk = sqlite3.connect('/tmp/ramdisk/kanomonitor_live.db') 
    cursor = conn_ramdisk.execute('SELECT * FROM aanwezig')
    for e in cursor:
        print (e)
    conn_ramdisk.close
    time.sleep(30)

