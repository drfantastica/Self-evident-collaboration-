import asyncio
from bleak import BleakClient

async def scan():
    address = "B1569DC4-2F2F-85E6-E210-A3A56BC1D50C"
    async with BleakClient(address) as client:
        print(f"Connected to device: {client.address}")
        services = client.services
        for service in services:
            print(f"Service: {service.uuid}")
            for char in service.characteristics:
                print(f"Characteristic: {char.uuid}")
                if char.uuid == "0000110A-0000-1000-8000-00805F9B34FB":  # Example RSSI characteristic
                    rssi = await client.read_gatt_char(char.uuid)
                    print(f"RSSI: {rssi}")

asyncio.run(scan())