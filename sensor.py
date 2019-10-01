import smbus2
import bme280
import asyncio
import time
import json
import RPi.GPIO as GPIO
from azure.iot.device.aio import IoTHubDeviceClient

port = 1
address = 0x77
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)

def get_temp():
    data = bme280.sample(bus, address, calibration_params)
    return data.temperature

def handle_twin(twin):
    print("Twin received", twin)
    if ('desired' in twin):
        desired = twin['desired']
        if ('led' in desired):
            GPIO.output(24, desired['led'])

async def main():

    conn_str = "<Your device connection string goes here>"
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
    await device_client.connect()

    last_temp = ""

    while True:
        temp = "{0:0.1f}".format(get_temp())
        print("Temperature", temp)

        if temp != last_temp:
            last_temp = temp;

            data = {}
            data['temperature'] = temp
            json_body = json.dumps(data)
            print("Sending message: ", json_body)
            await device_client.send_message(json_body)

        twin = await device_client.get_twin()
        handle_twin(twin)

        time.sleep(1)

    await device_client.disconnect()



if __name__ == "__main__":
    asyncio.run(main())