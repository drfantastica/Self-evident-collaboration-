#!/bin/zsh
# Fixed BLE test with proper asyncio handling
python3 <<EOF
import asyncio
from bleak import BleakScanner

def detection_callback(device, advertisement_data):
    if device.address == "B1569DC4-2F2F-85E6-E210-A3A56BC1D,0C":
        print(f"Found device: {device.name} ({device.address})")
        print(f"RSSI: {device.rssi} dBm")
        print(f"Service data: {advertisement_data.service_data}")

async def run_scanner():
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    try:
        await asyncio.sleep(30)  # Scan for 30 seconds
    finally:
        await scanner.stop()

asyncio.run(run_scanner())
EOF