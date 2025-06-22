# publisher.py
import json, time
import paho.mqtt.client as mqtt
from yoloinfer import run_yolo  # 你的YOLO推理函数
frames=1

BROKER = "localhost"
TOPIC= "iot/foggy"
client = mqtt.Client("edge-node")
client.connect(BROKER, 1883)
client.loop_start()
for img_path in [frames]:
    dets = run_yolo(img_path)
    payload = json.dumps({"ts": time.time(), "detections": dets})
    client.publish(TOPIC, payload, qos=1)
    time.sleep(0.5)


