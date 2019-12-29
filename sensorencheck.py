import sqlite3
import time
from datetime import datetime

x="1"
while (x=="1"):
    print(str(datetime.now()))
    conn_db = sqlite3.connect('kanomonitor.db')
    cursor = conn_db.execute('SELECT * FROM sensoren')
    for e in cursor:
        print (e)
    conn_db.close
    time.sleep(30)

