#!/usr/bin/python

import sqlite3
import datetime

conn = sqlite3.connect('kanomonitor.db')

print ("Opened database successfully")

sqlite_create_table_sensoren = '''CREATE TABLE SENSOREN
         (MAC TEXT PRIMARY KEY   NOT NULL,
         KANOID           TEXT    NOT NULL,
         STARTDATUM       timestamp NOT NULL,
         LAATSTGEZIEN	timestamp
	 );'''

sqlite_create_table_kanos = '''CREATE TABLE KANOS
         (KANOID TEXT PRIMARY KEY NOT NULL,
         KANONAAM           TEXT NOT NULL,
         KANOMERK           TEXT NOT NULL,
         KANOTYPE           TEXT NOT NULL, 
         KANOSOORT          TEXT NOT NULL,
         VAARGROEP          TEXT NOT NULL
         );'''

#kanotype, is typeaanduiding van fabrikant
#kanosooort is zeekano, vlakwater(wedstrijd) etc.

sqlite_create_table_uitgeleend = '''CREATE TABLE UITGELEEND
         (STARTTIJD timestamp PRIMARY KEY   NOT NULL,
         EINDTIJD timestamp NOT NULL,
         MAC  TEXT NOT NULL
         );'''



conn.execute (sqlite_create_table_sensoren)
conn.execute (sqlite_create_table_kanos)
conn.execute (sqlite_create_table_uitgeleend)
print ("Table created successfully")

conn.close()
