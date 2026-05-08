#!/bin/bash
# R1 BLE setup script
set -e

cd ~/local_media_index/r1_ble/
python3 discover.py --name 'ihoment_H5083_85B5'
python3 probe.py
bash run.sh

python3 probe.py

# Final confirmation
signal latch "R1 BLE probe and config completed. Gesture map set: tap=Resonance, scroll=Interference, long-press=Note. Server and listener running."

exit 0