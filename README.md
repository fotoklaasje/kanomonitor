# kanomonitor
this monitors when kajaks have left the storage by use of BLE beaons
uses a database on a ramdisk for current presence (to minimise sd card write on raspberry pi), and logs historical presence in a database on sd card.

dependancies:
apt:
-python3 
-python3-dev
-python3-pip
-sqlite3
-git

pip3:
-aiocron
-aioble
-aioblescan

we also need a tmpfs partiton for the current status database at /tmp/ramdisk/
fstab:
tmpfs /tmp/ramdisk tmpfs nosuid,nodev,noatime,size=20M 0 0

git clone https://github.com/fotoklaasje/kanomonitor.git
sudo python3 maak_database.py

copy KanomonitorBackend.service to /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable KanomonitorBackend
sudo systemctl start KanomonitorBackend
