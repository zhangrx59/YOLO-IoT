# monitor_app.py
from f import Flask, request, jsonify
import threading, queue, json
import paho.mqtt.client as mqtt

app = Flask(__name__)
q = queue.Queue()
@app.route('/stats')
def stats():
    return jsonify(count=q.qsize())
@app.route('/alerts')
def alerts():
    items = list(q.queue)
    return jsonify(items)

def mqtt_thread():
    def on_msg(client, userdata, msg):
        data = json.loads(msg.payload)
        # 例如：检测到置信度 > 0.9 的“违规”类别时入队告警
        for d in data['detections']:
            if d['conf'] > 0.9 and d['class'] in ('car','person'):
                q.put({"ts": data['ts'], **d})
        # 始终把所有结果也放统计队列
        # q.put(data)
    client = mqtt.Client()
    client.connect("localhost", 1883)
    client.subscribe("iot/foggy")
    client.on_message = on_msg
    client.loop_forever()


if __name__ == "__main__":
    t = threading.Thread(target=mqtt_thread, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000)
