
#!/usr/bin/env python3 -*- coding:utf-8 -*-
#
# gebaseerd op voorbeeldscript voor aioblescan


import sys
import asyncio
import argparse
import re
import aioblescan as aiobs
import datetime
from datetime import datetime
from datetime import timedelta
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
maclijst = [] #macs in de database
kanolijst = {} # mac, en datetime laatste gezien - Ik zou het eigenlijk moeten herschrijven met die als dictionary
UitleenMinimum = timedelta(minutes=1)

def lees_maclijst():
    #lees de lijst met macs uit de database
    logging.debug("maclijst lezen")
    maclijst.append("6e:93:a3:36:63:7c")
    maclijst.append("56:ab:d5:06:12:87")
    maclijst.append("42:0b:26:63:9b:2e")
    maclijst.append("64:17:37:cd:10:f3")
    maclijst.append("73:8b:4a:21:85:d9")
    maclijst.append("f0:99:19:4b:28:81")
    maclijst.append("43:7f:a0:26:21:74")
    logger.debug(maclijst)
#def vandaaggezien():
    #schrijf voor alle kano's die vandaag gezien zijn mac adres en datum vandaag in de database

def schrijf_uitgeleend(mac_adres, uitleentijd, terugbrengtijd):
    logger.debug("leg vast in database, uitgeleend: ")
    logger.debug(mac_adres)
    logger.debug(uitleentijd)
    logger.debug(terugbrengtijd)
    # aanroepen als de kano terug gebracht is. schrijf in de database uitleentijd en terugbrengtijd
    
#def check_uitgeleend():
    #twijfelgevalletje? kijk of er kano's zijn die al meer dan 10 min weg zijn, en schrijf dat dan ergens weg zodat live gekeken kan worden wat er nu weg is.
    #misschien dit niet in lokale database opslaan, maar alleen op database op internet? (om sd kaart te ontlasten)


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
            logger.debug(gevonden_mac_adres)
            #kijken of hij in de maclijst staat
            if gevonden_mac_adres in maclijst:
                logger.debug("mac gevonden")
                #kijken of we hem al hebben gezien
                if gevonden_mac_adres in kanolijst: 
                    #logger.debug("update datum in kanolijst")
                    #kijk wanneer laatste datum
                    #als laatste datum meer dan 10 min geleden doe schrijf_uitgeleend
                    TijdNu = datetime.now()
                    if TijdNu - kanolijst[gevonden_mac_adres] > UitleenMinimum:
                        logger.debug("meer dan 10 min/uitleenminimum geleden")
                        schrijf_uitgeleend(gevonden_mac_adres, kanolijst[gevonden_mac_adres], TijdNu)
                    #update laatste datum
                    kanolijst[gevonden_mac_adres] = TijdNu
                    logger.debug("entry update")
                    logger.debug(gevonden_mac_adres)
                    logger.debug(kanolijst[gevonden_mac_adres])
                else:
                    logger.debug("voeg toe aan kanolijst")
                    kanolijst[gevonden_mac_adres]=datetime.now()
                    logger.debug("----")
                    logger.debug(kanolijst)
                    logger.debug("----")
                    #voeg mac toe aan kanolijst met nu als laatste datum
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
    conn.close()
    event_loop.close()
