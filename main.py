import json
import time
import paho.mqtt.client as mqttclient
import serial

print("IoT Gateway")

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883

mess = ""

THINGS_BOARD_ACCESS_TOKEN = "VvYKouCOZy2aIV0yHfWh"
bbc_port = "COM8"
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    # TODO: Add your source code to publish data to the server
    collect_data = {}
    if (splitData[1] == "TEMP"):
        collect_data["temperature"] = splitData[2]
    if (splitData[1] == "LIGHT"):
        collect_data["light"] = splitData[2]
    client.publish("v1/devices/me/telemetry", json.dumps(collect_data), 1)

# collect_data = {
#         'temperature': temp,
#         'humidity': humi,
#         'light': light_intesity,
#         # 'longitude': longitude,
#         # 'latitude': latitude,
#     }


def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        print(mess)
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd = 69
    # TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/BUTTON_LED',
                           json.dumps(temp_data), 1)
            if (jsonobj['params'] == True):
                cmd = 1
            else:
                cmd = 0
        if jsonobj['method'] == "setFAN":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/BUTTON_FAN',
                           json.dumps(temp_data), 1)
            if (jsonobj['params'] == True):
                cmd = 3
            else:
                cmd = 2
    except:
        pass

    if len(bbc_port) > 0:
        ser.write((str(cmd) + "#").encode())


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

while True:
    if len(bbc_port) > 0:
        readSerial()

    time.sleep(1)
