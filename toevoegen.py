#!/usr/bin/python

import sqlite3
import datetime

conn = sqlite3.connect('kanomonitor.db')

print ("Opened database successfully")

#maclijst = []

#maclijst.append("d8:a9:8b:b4:ea:18", datetime.datetime.now)
#maclijst.append("a8:1b:6a:ae:71:9f", )

#toevoegen = "INSERT INTO SENSOREN (MAC, KANOID, STARTDATUM) VALUES (\"a8:1b:6a:ae:71:9f\", 1 , \"" + datetime.datetime.now + "\")"

#conn.execute('insert into sensoren(MAC, KANOID, STARTDATUM) VALUES(?, ?, ?)', ("a8:1b:6a:ae:71:9f",1 , datetime.datetime.now() ) )
conn.execute('insert into sensoren(MAC, KANOID, STARTDATUM) VALUES(?, ?, ?)', ("f0:99:19:4b:28:81",1 , datetime.datetime.now() ) )

conn.commit()
conn.close()

conn = sqlite3.connect('kanomonitor.db')

print ("Opened database successfully")
#conn.execute('insert into kanos(kanoid, kanonaam, kanomerk, kanotype, kanosoort, vaargroep) VALUES(?, ?, ?,?,?,?)', (1,"zv1", "northshore", "shoreline", "zeekano", "zeegroep") )
conn.commit()
conn.close()
