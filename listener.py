# DEBUG: Characteristic monitoring
import logging
import asyncio
from bleak import BleakScanner

logging.basicConfig(level=logging.DEBUG)
CHAR_UUID = "0000110A-0000-1000-8000-00805F9B34FB"  # Example UUID

devices = asyncio.run(BleakScanner.discover())
logging.debug(f"Available devices: {devices}")

async def run():
    async with BleakClient("B1569DC4-2F2F-85E6-E210-A3A56BC1D50C") as client:
        services = await client.get_services()
        logging.debug(f"Discovered services: {services}")
        characteristic = client.get_characteristic(CHAR_UUID)
        if characteristic:
            value = await client.read_gatt_char(CHAR_UUID)
            logging.debug(f"Characteristic value: {value}")
        else:
            logging.error(f"Characteristic {CHAR_UUID} not found")

asyncio.run(run())
logging.debug(f'Available services: {device.services}'); logging.debug(f'Connecting to characteristic: {CHAR_UUID}'); characteristic = device.get_characteristic(CHAR_UUID); logging.debug(f'Characteristic value: {characteristic.value} if exists')