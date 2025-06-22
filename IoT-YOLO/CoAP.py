# coap_publisher.py
import asyncio, json
from aiocoap import Context, Message, POST
from yoloinfer import run_yolo

async def publish():
    protocol = await Context.create_client_context()
    dets = run_yolo("frame1.jpg")
    payload = json.dumps({"ts": asyncio.get_event_loop().time(),
                          "detections": dets}).encode()
    req = Message(code=POST,
                  uri="coap://localhost:5683/iot/foggy",
                  payload=payload)
    resp = await protocol.request(req).response
    print("Response:", resp.code)
if __name__ == "__main__":
    asyncio.run(publish())
