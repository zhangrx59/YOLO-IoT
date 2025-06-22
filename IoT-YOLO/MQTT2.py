# subscriber.py
import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    client.subscribe("iot/foggy", qos=1)
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(f"[{data['ts']}] 检测结果：{data['detections']}")
client = mqtt.Client("monitor")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883)
client.loop_forever()
