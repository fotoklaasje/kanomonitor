
#!/usr/bin/env python3 -*- coding:utf-8 -*-
#
# gebaseerd op voorbeeldscript voor aioblescan


import sys
import asyncio
import aiocron
import argparse
import re
import aioblescan as aiobs
import datetime
from datetime import datetime
from datetime import timedelta
import logging
import sqlite3
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
maclijst = [] #macs in de database
kanolijst = {} #dictionary mac als key, en datetime laatste gezien
UitleenMinimum = timedelta(minutes=1)

conn_ramdisk = sqlite3.connect('/tmp/ramdisk/kanomonitor_live.db')  

def lees_maclijst():
    #lees de lijst met macs uit de database
    #moet dit periodiek? (en dan ook de liveDB updaten?
    logging.debug("maclijst lezen")
    conn_db = sqlite3.connect('kanomonitor.db')
    cursor = conn_db.execute('SELECT MAC FROM sensoren')
    for e in cursor:
        if e[0] not in maclijst:
            maclijst.append(e[0])
    logger.debug(maclijst)
    conn_db.close

def maak_live_db():
    sqlite_create_table_aanwezig = '''CREATE TABLE AANWEZIG
         (KANOID TEXT PRIMARY KEY   NOT NULL,
         MAC             TEXT NOT NULL,
         KANONAAM           TEXT NOT NULL,
         KANOMERK           TEXT NOT NULL,
         KANOTYPE           TEXT NOT NULL,
         KANOSOORT          TEXT NOT NULL,
         VAARGROEP          TEXT NOT NULL,
         AANWEZIG           INT NOT NULL
	 );'''
    logger.debug("live db tabel wordt gemaakt")
    try:
        conn_ramdisk.execute("DELETE FROM aanwezig")
    except Exception as x:
        conn_ramdisk.execute(sqlite_create_table_aanwezig)


def voeg_aan_live_db_toe():
    #kopieer kano's uit de echte database met meest recente mac adres
    sqlite_kano_meest_recente_mac = '''select s1.kanoid, mac, kanonaam, kanomerk, kanotype, kanosoort, vaargroep
        from sensoren s1
	join kanos
	on s1.kanoid = kanos.kanoid
	WHERE  startdatum=(SELECT MAX(s2.startdatum)
              FROM sensoren s2
              WHERE s1.kanoid = s2.kanoid);'''
    conn_db = sqlite3.connect('kanomonitor.db')
    cursor_ramdisk = conn_ramdisk.execute('select kanoid, mac from aanwezig')
    ramdisk_lijst_id = []
    ramdisk_lijst_mac = []
    for row in cursor_ramdisk:
        ramdisk_lijst_id.append(row[0])
        ramdisk_lijst_mac.append(row[1])
    cursor = conn_db.execute(sqlite_kano_meest_recente_mac)
    for row in cursor:
        if row[0] not in ramdisk_lijst_id:
            logger.debug("rij toevoegen aan live database")
            logger.debug(row[0])
            sqlite_invoegen_in_ramdisk = '''insert into aanwezig
            (kanoid, mac, kanonaam, kanomerk, kanotype, kanosoort, vaargroep, aanwezig)
            values (?,?,?,?,?,?,?,?);'''
            conn_ramdisk.execute(sqlite_invoegen_in_ramdisk, (row[0], row[1], row[2], row[3], row[4], row[5], row[6], "0"))
        #als de kano een nieuwe sensor heeft gekregen
        elif row[1] not in ramdisk_lijst_mac:
            logger.debug("mac updaten naar nieuwste")
            sqlite_update_mac = 'update aanwezig set mac = "' + row[1] + '" where kanoid = "' + row[0] + '";'
            conn_ramdisk.execute(sqlite_update_mac)
    conn_db.close()
    conn_ramdisk.commit()

def live_database_aanwezigheid(mac, status):
    sqlite_update_mac_aanwezig = 'update aanwezig set aanwezig = "' + status + '" where mac = "' + mac + '";'
    conn_ramdisk.execute(sqlite_update_mac_aanwezig)
    conn_ramdisk.commit()

def wegtijd_verstreken(mac, tijdsduur):
    if datetime.now() - kanolijst[mac] > tijdsduur:
        return True
    else:
        return False

#@aiocron.crontab('*/15 * * * *')
#async def ieder_kwartier_uitvoeren():
#    voeg_aan_live_db_toe()
#    lees_maclijst()

@aiocron.crontab('* * * * *')
async def aiocron_testje():
    logger.debug("aiocron test")

#def vandaaggezien():
    #schrijf voor alle kano's die vandaag gezien zijn mac adres en datum vandaag in de database

def schrijf_uitgeleend(mac_adres, uitleentijd, terugbrengtijd):
    logger.debug("leg vast in database, uitgeleend: ")
    logger.debug(mac_adres)
    logger.debug(uitleentijd)
    logger.debug(terugbrengtijd)
    # aanroepen als de kano terug gebracht is. schrijf in de database uitleentijd en terugbrengtijd
    conn_db = sqlite3.connect('kanomonitor.db')
    conn_db.execute('insert into uitgeleend (STARTTIJD, EINDTIJD, MAC) VALUES(?, ?, ?);', (uitleentijd ,terugbrengtijd, mac_adres) )
    conn_db.commit()
    conn_db.close()
    #ook in live database schrijven dat de kano er weer is.
    live_database_aanwezigheid(mac_adres, "1")

#def check_uitgeleend():
    #twijfelgevalletje? kijk of er kano's zijn die al meer dan 10 min weg zijn, en schrijf dat dan ergens weg zodat live gekeken kan worden wat er nu weg is.
    #misschien dit niet in lokale database opslaan, maar alleen op database op internet? (om sd kaart te ontlasten)
    #kan ook in een lokale database op een ramdisk. 

def my_process(data):
    global opts

    ev=aiobs.HCI_Event()
    xx=ev.decode(data)
    #ev.show(0)
    
    # dit moet mooier kunnen met een functie die recursief door de lists naar .name = peer zoekt (inspiratie https://thispointer.com/python-convert-list-of-lists-or-nested-list-to-flat-list/ )
    # onderstaande manier met ev.retrieve werkt eleganter maar bied geen manier om major en minor te lezen
    try:
        mac = ev.retrieve("peer")
        for x in mac:
            gevonden_mac_adres = x.val
            #logger.debug(gevonden_mac_adres)
            #kijken of hij in de maclijst staat
            if gevonden_mac_adres in maclijst:
                #logger.debug("mac gevonden")
                #kijken of we hem al hebben gezien
                if gevonden_mac_adres in kanolijst: 
                    #logger.debug("update datum in kanolijst")
                    #kijk wanneer laatste datum
                    #als laatste datum meer dan 10 min geleden doe schrijf_uitgeleend
                    TijdNu = datetime.now()
                    if wegtijd_verstreken(gevonden_mac_adres, UitleenMinimum):
                        logger.debug("meer dan 10 min/uitleenminimum geleden")
                        schrijf_uitgeleend(gevonden_mac_adres, kanolijst[gevonden_mac_adres], datetime.now())
                    #update laatste datum
                    kanolijst[gevonden_mac_adres] = TijdNu
                    logger.debug("entry update")
                    logger.debug(gevonden_mac_adres)
                    logger.debug(kanolijst[gevonden_mac_adres])
                else:
                    #voeg mac toe aan kanolijst met nu als laatste datum  
                    logger.debug("voeg toe aan kanolijst")
                    kanolijst[gevonden_mac_adres]=datetime.now()
                    logger.debug("----")
                    logger.debug(kanolijst)
                    logger.debug("----")
                    #melden als aanwezig in lived database
                    live_database_aanwezigheid(gevonden_mac_adres, "1")
    except Exception as ex:
        logger.debug(ex)

event_loop = asyncio.get_event_loop()

#First create and configure a raw socket
mysocket = aiobs.create_bt_socket()

#create a connection with the raw socket
#This used to work but now requires a STREAM socket.
#fac=event_loop.create_connection(aiobs.BLEScanRequester,sock=mysocket)
#Thanks to martensjacobs for this fix
fac=event_loop._create_connection_transport(mysocket,aiobs.BLEScanRequester,None,None)
#Start it
conn,btctrl = event_loop.run_until_complete(fac)
#Attach your processing
btctrl.process=my_process

#als we dagelijks willen kijken of bepaalde kano's al lang niet gezien zijn (batterij leeg?) dan kan dat met aiocron https://github.com/gawel/aiocron
#ook goed om periodiek lijst met MAC's op te halen die geregistreerd moeten worden (zodat niet elke passant in de database beland)

#Probe

#print(datetime.now())
#kanolijst[0].append("00:00:00:00:00:00")
#kanolijst[0][1] = datetime.now()
lees_maclijst()
maak_live_db()
voeg_aan_live_db_toe()
btctrl.send_scan_request()
try:
    #event_loop.run_until_complete(event_loop.future)
    event_loop.run_forever()
except KeyboardInterrupt:
    logger.debug('keyboard interrupt')
finally:
    logger.debug('closing event loop')
    btctrl.stop_scan_request()
    command = aiobs.HCI_Cmd_LE_Advertise(enable=False)
    btctrl.send_command(command)
    conn_ramdisk.close()
    conn.close()
    event_loop.close()
