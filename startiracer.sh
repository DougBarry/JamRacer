#!/bin/bash
# Pair with Arexx iRacer/Dagu car
echo "1234" | sudo bluez-simple-agent hci0 00:12:05:09:96:64

# Ensure simple-agent mode is avaiable for pairing to NXT device
sudo bluez-simple-agent hci0 68:86:e7:00:dc:72

# Run JamRacer as root to avoid problems with Bluetooth
sudo python JamRacerMain.py 