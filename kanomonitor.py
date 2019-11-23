#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# This application is an example on how to use aioblescan
#
# Copyright (c) 2017 François Wautier
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
#testje1
import sys
import asyncio
import argparse
import re
import aioblescan as aiobs
maclijst = [] #macs in de database
#kanolijst = [[],[]] # mac, en datetime laatste gezien

def lees_maclijst():
    #lees de lijst met macs uit de database
    print ("maclijst lezen")
    maclijst.append("6e:93:a3:36:63:7c")
    maclijst.append("56:ab:d5:06:12:87")
    print (maclijst)
#def vandaaggezien():
    #schrijf voor alle kano's die vandaag gezien zijn mac adres en datum vandaag in de database

#def schrijf_uitgeleend(mac_adres, uitleentijd, terugbrengtijd):
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
        #print (ev.payload[2].payload[1].payload[3].val)
        mac = ev.retrieve("peer")
        for x in mac:
            mac_adres_gevonden = str(x.val)
            print (mac_adres_gevonden)
            print (type(mac_adres_gevonden))
            print(type(maclijst[0]))
            print (type(x.val))
            #kijken of hij in de maclijst staat
            if mac_adres_gevonden in maclijst:
                print ("mac gevonden")
                #kijken of we hem al hebben gezien
                #if mac_adres_gevonden in kanolijst[1]:
                #    print ("update datum in kanolijst")
                    #vind locatie in lijst
                    #kijk wanneer laatste datum
                    #als laatste datum meer dan 10 min geleden doe schrijf_uitgeleend
                    #anders update laatste datum
                #else:
                #    print ("voeg toe aan kanolijst")
                    #voeg mac toe aan kanolijst met nu als laatste datum
    except:
        print ("geen payload")

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
lees_maclijst()
btctrl.send_scan_request()
try:
    #event_loop.run_until_complete(event_loop.future)
    event_loop.run_forever()
except KeyboardInterrupt:
    print('keyboard interrupt')
finally:
    print('closing event loop')
    btctrl.stop_scan_request()
    command = aiobs.HCI_Cmd_LE_Advertise(enable=False)
    btctrl.send_command(command)
    conn.close()
    event_loop.close()
